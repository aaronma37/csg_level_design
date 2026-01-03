import cv2
import numpy as np
import json
import math
import sys
import os

# Import VoxelModel from csg_compiler
sys.path.append(os.path.join(os.getcwd(), ".."))
try:
    from csg_compiler import VoxelModel
except ImportError:
    print("Error: Could not import csg_compiler. Ensure it is in the current directory.")
    sys.exit(1)

def reconstruct(video_path, metadata_path, output_path="reconstructed_model.vox", grid_size=128):
    # 1. Load Metadata
    with open(metadata_path, 'r') as f:
        meta = json.load(f)
    
    bg_color = np.array(meta["background_color"])
    palette_colors = meta["palette"]
    # Trust the Phase 1 estimate
    pixels_per_voxel = meta["pixels_per_voxel"] 
    estimated_height = int(meta["height"] / pixels_per_voxel)
    
    print(f"Reconstruction Config: {pixels_per_voxel} px/voxel, Grid: {grid_size}")

    # 2. Setup Voxel Model & Palette
    model = VoxelModel()
    color_to_index = {}
    palette_tuples = [tuple(c) for c in palette_colors]
    if not palette_tuples: palette_tuples = [(128, 128, 128)]
    
    # Fill palette
    for i, c in enumerate(palette_tuples):
        if i + 1 < 256:
            model.palette[i+1] = tuple(c) + (255,)
            color_to_index[tuple(c)] = i + 1

    def get_nearest_color_index(rgb):
        best_dist = float('inf')
        best_idx = 1
        for c_tuple, idx in color_to_index.items():
            dist = sum((a-b)**2 for a,b in zip(rgb, c_tuple))
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        return best_idx
        
    def is_close_to_palette(rgb, threshold=40):
        # Is this color close to ANY known palette color?
        for c_tuple in color_to_index.keys():
            if np.linalg.norm(np.array(rgb) - np.array(c_tuple)) < threshold:
                return True
        return False

    # 3. Process Video Frames
    cap = cv2.VideoCapture(video_path)
    frames = []
    masks = []
    
    total_frames = meta["total_frames"]
    stride = max(1, total_frames // 48)
    
    print(f"Loading frames (stride {stride})...")
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if frame_idx % stride == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            
            # --- HSV MASKING ---
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            # Background is White: High Value, Low Saturation.
            # Skin is: High Value, Medium Saturation.
            # Dark is: Low Value.
            
            # We want to keep anything that is NOT Background.
            # Background Definition: Saturation < 20 AND Value > 200 (Adjusted for white BG)
            # But wait, BG might be noisy.
            # Let's define Object:
            # 1. Saturation > 15 (Has color)
            # OR
            # 2. Value < 200 (Is dark)
            
            s = hsv[:,:,1]
            v = hsv[:,:,2]
            
            is_foreground = (s > 15) | (v < 220)
            
            # Clean up
            mask = is_foreground.astype(np.uint8)
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.dilate(mask, kernel, iterations=1)
            mask = mask.astype(bool)
            masks.append(mask)
            
        frame_idx += 1
    cap.release()
    
    num_views = len(frames)
    width = meta["width"]
    height = meta["height"]
    cx = width / 2
    cy = height / 2
    
    # 4. Phase 1: Visual Hull (Strict Carving)
    print("Building Visual Hull (Carving)...")
    # Start with full grid? No, efficient iteration.
    # We'll build a set of candidate voxels.
    
    candidate_voxels = []
    offset = grid_size // 2
    
    # Optimization: Bounding Box
    # Only iterate where masks are present?
    # For now, just iterate grid.
    
    for x in range(-offset, offset):
        for z in range(-offset, offset):
            for y in range(-offset, offset):
                
                # Check ALL masks
                is_visible = True
                
                for i in range(num_views):
                    angle = (i * stride / total_frames) * 2 * math.pi
                    rx = x * math.cos(angle) - z * math.sin(angle)
                    # rz = x * math.sin(angle) + z * math.cos(angle)
                    
                    u = int(rx * pixels_per_voxel + cx)
                    v = int(-y * pixels_per_voxel + cy)
                    
                    if 0 <= u < width and 0 <= v < height:
                        if not masks[i][v, u]:
                            is_visible = False
                            break
                    else:
                        # Out of frame? Assume empty if background is white/infinite.
                        # Usually safest to assume empty if out of bounds.
                        is_visible = False
                        break
                
                if is_visible:
                    candidate_voxels.append((x, y, z))

    print(f"Visual Hull: {len(candidate_voxels)} voxels.")
    
    # --- CALCULATE VOXEL NORMALS ---
    voxel_set = set(candidate_voxels)
    voxel_normals = {}
    
    print("Calculating Normals...")
    for (x, y, z) in candidate_voxels:
        # Simple neighbor-based normal estimation
        nx = (1 if (x-1, y, z) not in voxel_set else 0) - (1 if (x+1, y, z) not in voxel_set else 0)
        ny = (1 if (x, y-1, z) not in voxel_set else 0) - (1 if (x, y+1, z) not in voxel_set else 0)
        nz = (1 if (x, y, z-1) not in voxel_set else 0) - (1 if (x, y, z+1) not in voxel_set else 0)
        
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 0:
            voxel_normals[(x,y,z)] = (nx/length, ny/length, nz/length)
        else:
            voxel_normals[(x,y,z)] = (0, 0, 0)

    # 5. Phase 2: Occlusion-Aware & Normal-Weighted Coloring
    print("Refining Colors with Occlusion & Normals...")
    
    # Accumulate (R*w, G*w, B*w, Weight)
    voxel_color_accum = {v: [0.0, 0.0, 0.0, 0.0] for v in candidate_voxels}
    
    for i in range(num_views):
        angle = -(i * stride / total_frames) * 2 * math.pi
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 1. Build Depth Buffer (Min Depth = Closest to Camera)
        depth_buffer = {}
        projections = {}
        
        for (x, y, z) in candidate_voxels:
            rx = x * cos_a - z * sin_a
            rz = x * sin_a + z * cos_a
            
            # Mirror X (Flip horizontal) to match video orientation
            u = int(-rx * pixels_per_voxel + cx)
            v = int(-y * pixels_per_voxel + cy)
            
            if 0 <= u < width and 0 <= v < height:
                depth = rz
                projections[(x,y,z)] = (u, v, depth)
                
                # Keep MIN depth (closest to camera)
                if (u,v) not in depth_buffer or depth < depth_buffer[(u,v)]:
                    depth_buffer[(u,v)] = depth
        
        # 2. Accumulate Colors
        for (x, y, z), (u, v, depth) in projections.items():
            min_depth = depth_buffer[(u,v)]
            if depth <= min_depth + 2.0:
                 pixel = frames[i][v, u]
                 
                 # Normal Weighting
                 nx, ny, nz = voxel_normals[(x,y,z)]
                 
                 # Rotate Normal to View Space (Camera looks -Z, View Vector (0,0,1))
                 # Rotation: 
                 # nx_rot = nx * cos - nz * sin
                 # nz_rot = nx * sin + nz * cos
                 
                 # The 'rx, rz' logic used: rx = x*cos - z*sin
                 # So normal rotates the same way.
                 
                 nrz = nx * sin_a + nz * cos_a
                 
                 # View Vector is (0,0,1) in this rotated frame (towards camera)
                 # Wait, Camera is at -Infinity Looking +Z?
                 # If Camera at -Inf, Surface must point -Z to be seen.
                 # So Dot should be Negative.
                 
                 dot = nrz
                 if dot < -0.1: # Only face-forward views (Normal points -Z)
                     weight = dot * dot # Sharpen contribution
                     
                     accum = voxel_color_accum[(x,y,z)]
                     accum[0] += pixel[0] * weight
                     accum[1] += pixel[1] * weight
                     accum[2] += pixel[2] * weight
                     accum[3] += weight

    # 3. Finalize Colors
    final_voxels = {}
    
    for (x, y, z), accum in voxel_color_accum.items():
        total_weight = accum[3]
        if total_weight <= 0.001: continue 
        
        mean_col = (accum[0]/total_weight, accum[1]/total_weight, accum[2]/total_weight)
        final_voxels[(x, y, z)] = mean_col

    print(f"Final Count: {len(final_voxels)}")

    # 6. Save with Offset Info
    # Calculate bounds logic from csg_compiler to print offsets
    if final_voxels:
        keys = list(final_voxels.keys())
        # MagicaVoxel Save Order: X=x, Y=z, Z=y
        # But we pass (x,z,y) to model.voxels
        # So we check x, z, y
        
        xs = [k[0] for k in keys]
        zs = [k[1] for k in keys] # saved as Y
        ys = [k[2] for k in keys] # saved as Z
        
        min_x = min(xs)
        min_y = min(zs) # Note: Z here matches Y in file
        min_z = min(ys) # Note: Y here matches Z in file
        
        print(f"SAVE_OFFSET: {min_x} {min_y} {min_z}")
    
    for (x,y,z), color in final_voxels.items():
        idx = get_nearest_color_index(color)
        model.voxels[(x, z, y)] = idx # Swap Y/Z for MagicaVoxel
        
    model.save(output_path)
    print("Done.")

if __name__ == "__main__":
    reconstruct("voxel_character.mp4", "video_metadata.json")