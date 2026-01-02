import cv2
import numpy as np
import sys

def debug_proj(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    indices = [0, total_frames//4, total_frames//2, 3*total_frames//4]
    
    # Camera Params (Must match space_carver.py)
    elevation_rad = 0.3
    dist = 6.0 
    f = 1.5
    
    # Points: Cube Corners + Axes
    points = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
        [0, 0, 0], # Center
        [0, 1, 0], # Up
        [0, 0, 1]  # Forward
    ]
    
    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret: break
        
        h, w, _ = frame.shape
        
        # Calculate angle for this frame
        angle_rad = 2 * np.pi * (idx / total_frames)
        
        # Same logic as space_carver
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
        
        K = np.array([
            [-f, 0, 0.5],
            [0, f, 0.5],
            [0, 0, 1]
        ])
        
        P = K @ extrinsic
        
        # Draw
        for pt in points:
            pt_h = np.array(pt + [1])
            uv_h = P @ pt_h
            if uv_h[2] == 0: continue
            
            u = uv_h[0] / uv_h[2]
            v = uv_h[1] / uv_h[2]
            
            u_px = int(u * w)
            v_px = int(v * h)
            
            color = (0, 255, 0)
            if pt == [0,0,0]: color = (0, 0, 255) # Red Center
            
            cv2.circle(frame, (u_px, v_px), 10, color, -1)
            
        filename = f"proj_check_{i}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")

if __name__ == "__main__":
    debug_proj(sys.argv[1])
