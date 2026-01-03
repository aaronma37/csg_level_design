import cv2
import numpy as np
import sys
import json
import os
import character_palette as palette # Use specific character palette
from csg_compiler import VoxelModel

def load_palette():
    pal = []
    for i in range(256):
        try:
            col = palette.PALETTE_COLORS[i]
        except IndexError:
            col = (0, 0, 0, 0)
        pal.append(col)
    return np.array(pal, dtype=np.uint8)

def get_closest_palette_index(rgb_val, palette_arr):
    diff = palette_arr[:, :3].astype(int) - rgb_val.astype(int)
    dist_sq = np.sum(diff**2, axis=1).astype(float)
    dist_sq[palette_arr[:, 3] < 128] = np.inf
    return np.argmin(dist_sq)

class SpaceCarver:
    def __init__(self, video_path, resolution=64):
        self.video_path = video_path
        self.res = resolution
        self.voxels = np.ones((resolution, resolution, resolution), dtype=bool)
        self.colors = np.zeros((resolution, resolution, resolution, 3), dtype=np.float32)
        self.counts = np.zeros((resolution, resolution, resolution), dtype=np.float32)
        
        self.bounds_min = -1.3
        self.bounds_max = 1.3

    def load_frames(self, limit=None):
        cap = cv2.VideoCapture(self.video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            if limit and len(frames) >= limit: break
        cap.release()
        print(f"Loaded {len(frames)} frames.")
        return frames

    def get_projection_matrix(self, angle_rad, elevation_rad=0.3):
        dist = 6.0 
        cx = dist * np.sin(angle_rad) * np.cos(elevation_rad)
        cz = dist * np.cos(angle_rad) * np.cos(elevation_rad)
        cy = dist * np.sin(elevation_rad)
        cam_pos = np.array([cx, cy, cz])
        target = np.array([0, 0, 0])
        up = np.array([0, 1, 0])
        z_axis = (cam_pos - target)
        z_axis = z_axis / np.linalg.norm(z_axis)
        x_axis = np.cross(up, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)
        R = np.array([x_axis, y_axis, z_axis])
        t = -R @ cam_pos
        extrinsic = np.hstack((R, t.reshape(3,1)))
        f = 1.5
        K = np.array([[-f, 0, 0.5], [0, f, 0.5], [0, 0, 1]])
        return K @ extrinsic

    def project_voxels(self, P, width, height):
        x = np.linspace(self.bounds_min, self.bounds_max, self.res)
        y = np.linspace(self.bounds_min, self.bounds_max, self.res)
        z = np.linspace(self.bounds_min, self.bounds_max, self.res)
        xv, yv, zv = np.meshgrid(x, y, z, indexing='ij')
        points = np.vstack((xv.flatten(), yv.flatten(), zv.flatten(), np.ones(xv.size)))
        uv_h = P @ points
        u = uv_h[0] / (uv_h[2] + 1e-5)
        v = uv_h[1] / (uv_h[2] + 1e-5)
        u_px = (u * width).astype(int)
        v_px = (v * height).astype(int)
        return u_px, v_px, uv_h[2]

    def get_background_mask(self, frame):
        is_black = np.all(frame < 10, axis=2)
        is_white = np.all(frame > 250, axis=2)
        candidate_bg = (is_black | is_white).astype(np.uint8)
        h, w = candidate_bg.shape
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(candidate_bg, connectivity=4)
        bg_mask = np.zeros((h, w), dtype=bool)
        for i in range(1, num_labels):
            x, y, wa, ha, area = stats[i]
            if x == 0 or y == 0 or (x + wa) == w or (y + ha) == h:
                bg_mask[labels == i] = True
        return bg_mask

    def quantize_colors(self, colors, k=10):
        if len(colors) < k: return colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness, labels, centers = cv2.kmeans(colors, k, None, criteria, 10, flags)
        return centers[labels.flatten()]

    def carve(self, use_photoconsistency=False):
        frames = self.load_frames()
        if not frames: return
        h, w, _ = frames[0].shape
        total_frames = len(frames)
        
        print("Starting Visual Hull Pass (Flood Fill)...")
        valid_mask = self.voxels.flatten()
        for i, frame in enumerate(frames):
            angle = -2 * np.pi * (i / total_frames)
            P = self.get_projection_matrix(angle)
            u, v, depth = self.project_voxels(P, w, h)
            in_frame = (u >= 0) & (u < w) & (v >= 0) & (v < h) & (depth < 0)
            valid_indices = np.where(in_frame & valid_mask)[0]
            if len(valid_indices) == 0: continue
            bg_mask = self.get_background_mask(frame)
            pix_u, pix_v = np.clip(u[valid_indices], 0, w-1), np.clip(v[valid_indices], 0, h-1)
            is_background = bg_mask[pix_v, pix_u]
            valid_mask[valid_indices[is_background]] = False
            if i % 20 == 0:
                print(f"Processed frame {i}/{total_frames}. Voxels remaining: {np.sum(valid_mask)}")

        self.voxels = valid_mask.reshape(self.res, self.res, self.res)
        
        if use_photoconsistency:
            print("Starting Photoconsistency Pass (Robust Median/IQR)...")
            step = 8
            view_indices = list(range(0, total_frames, step))
            num_views = len(view_indices)
            
            for pass_idx in range(3):
                print(f"--- Pass {pass_idx+1}/3 ---")
                valid_mask = self.voxels.flatten()
                voxel_samples = np.full((len(valid_mask), num_views, 3), -1, dtype=np.int16)
                sample_counts = np.zeros(len(valid_mask), dtype=int)
                
                # Consistency thresholds - squared Euclidean distance
                dist_thresh_sq = 1200 
                
                # Accumulate consistency counts
                # Using simple pairwise distance approach?
                # No, we switched to Cluster Consistency in previous turns but I reverted to median/IQR in recent replacement?
                # Actually, the user liked "Option 3" (Texture Reprojection) which used clustering.
                # So I should keep the CLUSTERING logic here.
                
                # Re-implementing Cluster-Based logic for robustness
                
                # 1. Collect samples
                for view_idx, frame_idx in enumerate(view_indices):
                    frame = frames[frame_idx]
                    angle = -2 * np.pi * (frame_idx / total_frames)
                    P = self.get_projection_matrix(angle)
                    u, v, depth = self.project_voxels(P, w, h)
                    
                    in_view = (u >= 0) & (u < w) & (v >= 0) & (v < h) & (depth < 0) & valid_mask
                    curr_view_indices = np.where(in_view)[0]
                    if len(curr_view_indices) == 0: continue
                    vu, vv, vd = u[curr_view_indices], v[curr_view_indices], depth[curr_view_indices]
                    
                    z_buffer = np.full((h, w), -np.inf, dtype=np.float32)
                    pixel_idx = vv * w + vu
                    np.maximum.at(z_buffer.ravel(), pixel_idx, vd)
                    visible = vd >= (z_buffer.ravel()[pixel_idx] - 0.05)
                    visible_indices = curr_view_indices[visible]
                    if len(visible_indices) == 0: continue
                    
                    pix_u, pix_v = np.clip(u[visible_indices], 0, w-2), np.clip(v[visible_indices], 0, h-2)
                    c00 = frame[pix_v, pix_u].astype(np.float32)
                    c01 = frame[pix_v, pix_u+1].astype(np.float32)
                    c10 = frame[pix_v+1, pix_u].astype(np.float32)
                    c11 = frame[pix_v+1, pix_u+1].astype(np.float32)
                    cols = (c00 + c01 + c10 + c11) * 0.25
                    voxel_samples[visible_indices, view_idx] = cols.astype(np.int16)
                    sample_counts[visible_indices] += 1

                # 2. Analyze Clusters
                has_samples = sample_counts > 3
                cand_indices = np.where(has_samples)[0]
                if len(cand_indices) == 0: break
                
                cand_samples = voxel_samples[cand_indices]
                cand_samples_f = cand_samples.astype(np.float32)
                cand_samples_f[cand_samples == -1] = np.nan
                
                # Pairwise Distance
                # A: (N, V, 1, 3)
                A = cand_samples_f[:, :, None, :]
                B = cand_samples_f[:, None, :, :]
                diff_sq = np.sum((A - B)**2, axis=-1) # (N, V, V)
                
                adj = diff_sq < dist_thresh_sq
                support_counts = np.sum(adj, axis=2)
                max_support = np.max(support_counts, axis=1)
                best_view_indices = np.argmax(support_counts, axis=1)
                
                # Calculate color
                cluster_mask = adj[np.arange(len(cand_indices)), best_view_indices, :]
                cluster_vals = np.nan_to_num(cand_samples_f) * cluster_mask[..., None]
                final_colors = np.sum(cluster_vals, axis=1) / np.maximum(np.sum(cluster_mask, axis=1)[..., None], 1)
                
                # Thresholds (Relaxed: 10/6)
                y_indices = (cand_indices // self.res) % self.res
                y_vals = self.bounds_min + (y_indices / (self.res - 1)) * (self.bounds_max - self.bounds_min)
                min_views = np.where(y_vals > 0.4, 6, 10)
                
                bad_voxels = max_support < min_views
                
                remove_indices = cand_indices[bad_voxels]
                valid_mask[remove_indices] = False
                print(f"Pass {pass_idx+1}: Carved {len(remove_indices)} voxels (Cluster < {6}/{10}).")
                self.voxels = valid_mask.reshape(self.res, self.res, self.res)
                
                if pass_idx == 2 or len(remove_indices) < 100:
                    survivor_indices = cand_indices[~bad_voxels]
                    valid_final_colors = final_colors[~bad_voxels]
                    flat_colors = self.colors.reshape(-1, 3)
                    flat_colors[survivor_indices] = valid_final_colors
                    self.counts.flat[survivor_indices] = 1
                    if len(remove_indices) < 100: break

    def morphological_closing(self):
        print("Post-processing: Morphological Closing (Dilate + Erode)...")
        grid = self.voxels
        padded = np.pad(grid, 1, mode='constant', constant_values=0)
        # Dilation
        neighbors = (padded[:-2, 1:-1, 1:-1] | padded[2:, 1:-1, 1:-1] | 
                     padded[1:-1, :-2, 1:-1] | padded[1:-1, 2:, 1:-1] | 
                     padded[1:-1, 1:-1, :-2] | padded[1:-1, 1:-1, 2:])
        dilated = grid | neighbors
        
        # Erosion of Dilated
        padded_d = np.pad(dilated, 1, mode='constant', constant_values=0)
        neighbors_d = (padded_d[:-2, 1:-1, 1:-1] & padded_d[2:, 1:-1, 1:-1] & 
                       padded_d[1:-1, :-2, 1:-1] & padded_d[1:-1, 2:, 1:-1] & 
                       padded_d[1:-1, 1:-1, :-2] & padded_d[1:-1, 1:-1, 2:])
        closed = neighbors_d
        
        added_count = np.sum(closed & ~grid)
        print(f"Closed gaps: Added {added_count} voxels.")
        self.voxels = closed
        
        if added_count > 0:
            # Simple color fill: set to grey/average? 
            # We rely on smooth_colors to propagate color later.
            # But let's init with neighbors
            pass

    def smooth_colors(self):
        # Disabled to keep voxel art crisp
        pass

    def save_vox(self, output_path):
        self.morphological_closing()
        # self.smooth_colors() # Disabled
        
        valid = self.voxels
        avg_colors = self.colors
        
        print("Post-processing: Boosting saturation...")
        rgb = avg_colors[valid]
        lum = (0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2])[:, None]
        avg_colors[valid] = np.clip(lum + (rgb - lum) * 1.2, 0, 255)
        
        print("Post-processing: Quantizing colors...")
        flat_colors = avg_colors.reshape(-1, 3)
        valid_indices = np.where(valid.flatten())[0]
        flat_colors[valid_indices] = self.quantize_colors(flat_colors[valid_indices], k=12)
        
        pal_arr = load_palette()
        model = VoxelModel(custom_palette=palette.PALETTE_COLORS)
        print("Mapping colors to palette and building VOX...")
        count = 0
        for x, y, z in zip(*np.where(valid)):
            pal_idx = get_closest_palette_index(avg_colors[x, y, z], pal_arr)
            if pal_idx > 0:
                model.voxels[(x, z, y)] = int(pal_idx)
                count += 1
        print(f"Final Voxel Count: {count}")
        model.save(output_path)

if __name__ == "__main__":
    vid_file, out_file = sys.argv[1], sys.argv[2]
    res = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    check = sys.argv[4] == "1" if len(sys.argv) > 4 else False
    carver = SpaceCarver(vid_file, res)
    carver.carve(use_photoconsistency=check)
    carver.save_vox(out_file)