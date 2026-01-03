import cv2
import numpy as np
import json
import math
import sys
import os

# Import VoxelModel
sys.path.append(os.path.join(os.getcwd(), ".."))
try:
    from csg_compiler import VoxelModel
except ImportError:
    print("Error: Could not import csg_compiler.")
    sys.exit(1)

def load_vox_file(filename):
    with open(filename, 'rb') as f:
        magic = f.read(4)
        version = f.read(4)
        voxels = {} 
        palette = []
        
        raw_voxels = []
        
        while True:
            try:
                chunk_id = f.read(4)
                if not chunk_id: break
                content_size = int.from_bytes(f.read(4), 'little')
                children_size = int.from_bytes(f.read(4), 'little')
                content = f.read(content_size)
                if chunk_id == b'XYZI':
                    num_voxels = int.from_bytes(content[:4], 'little')
                    for i in range(num_voxels):
                        x = content[4+i*4]
                        y = content[4+i*4+1]
                        z = content[4+i*4+2]
                        c = content[4+i*4+3]
                        # Raw load: X, Y, Z
                        raw_voxels.append((x, y, z, c))
                        
                elif chunk_id == b'RGBA':
                    for i in range(256):
                        palette.append((content[i*4], content[i*4+1], content[i*4+2]))
            except: break
            
    # APPLY EXACT OFFSETS (Same as Refine Script)
    off_x = -12
    off_y = -25
    off_z = -18
    
    if raw_voxels:
        for x, y, z, c in raw_voxels:
            # Map back to Grid
            gx = x + off_x
            gy = z + off_y # File Z -> Grid Y
            gz = y + off_z # File Y -> Grid Z
            
            voxels[(gx, gy, gz)] = c

    return voxels, palette

def render_view(voxels, palette, width, height, angle, scale, bg_color):
    # Painter's Algorithm: Sort by depth (far to near)
    # Camera looks -Z. Rotated Z (rz) is depth.
    # We want to draw smallest Z (farthest) first?
    # Wait, in our rotation logic:
    # rx = x cos - z sin
    # rz = x sin + z cos
    # If camera is at -Z looking +Z.
    # Then LARGER rz is closer. 
    # So we draw SMALLEST rz first.
    
    # List of (depth, u, v, color)
    draw_list = []
    cx, cy = width / 2, height / 2
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    
    for (x,y,z), c_idx in voxels.items():
        # Rotation
        rx = x * cos_a - z * sin_a
        rz = x * sin_a + z * cos_a
        
        # Mirror X
        u = int(-rx * scale + cx)
        v = int(-y * scale + cy)
        
        # Color
        if c_idx > 0 and c_idx <= len(palette):
            c = palette[c_idx-1]
        else:
            c = (128,128,128)
            
        draw_list.append((rz, u, v, c))
        
    # Sort: Largest Z first (Closest to Camera)
    draw_list.sort(key=lambda p: p[0], reverse=True)
    
    # Draw
    canvas = np.full((height, width, 3), bg_color, dtype=np.uint8)
    
    # We draw squares for voxels. Size = scale.
    # To avoid gaps, maybe scale + 1?
    size = int(math.ceil(scale))
    offset = size // 2
    
    for depth, u, v, c in draw_list:
        # Check bounds roughly
        if u > -size and u < width+size and v > -size and v < height+size:
            # Draw rectangle
            # cv2.rectangle is slow for 80k calls?
            # Direct array access is faster but handles clipping poorly.
            # Let's use cv2.rectangle for safety.
            color_bgr = (int(c[2]), int(c[1]), int(c[0]))
            cv2.rectangle(canvas, (u-offset, v-offset), (u-offset+size, v-offset+size), color_bgr, -1)
            
    return canvas

def generate_debug_views(model_path, video_path, metadata_path):
    print(f"Generating debug views for {model_path}...")
    
    with open(metadata_path, 'r') as f:
        meta = json.load(f)
        
    voxels, palette = load_vox_file(model_path)
    if not palette: # Fallback
        palette = [(128,128,128)] * 256
        
    cap = cv2.VideoCapture(video_path)
    total_frames = meta["total_frames"]
    
    # Select 4 evenly spaced frames
    frame_indices = [0, total_frames//4, total_frames//2, 3*total_frames//4]
    
    output_images = []
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret: continue
        
        angle = -(idx / total_frames) * 2 * math.pi
        
        # Render
        rendered = render_view(
            voxels, palette, 
            meta["width"], meta["height"], 
            angle, 
            meta["pixels_per_voxel"], 
            tuple(meta["background_color"])
        )
        
        # Combine Side-by-Side
        combined = np.hstack((frame, rendered))
        
        # Add Text
        cv2.putText(combined, f"Frame {idx}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.putText(combined, "Render", (meta["width"] + 20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        filename = f"debug_frame_{idx}.png"
        cv2.imwrite(filename, combined)
        output_images.append(filename)
        print(f"Saved {filename}")
        
    return output_images

if __name__ == "__main__":
    # Debug the REFINED model
    generate_debug_views("refined_model.vox", "voxel_character.mp4", "video_metadata.json")