import cv2
import numpy as np
import json
import os
from collections import Counter
from sklearn.cluster import KMeans

def analyze_video(video_path, output_json="video_metadata.json"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")

    # 1. Detect Background
    sample_frames = []
    for i in range(0, total_frames, max(1, total_frames // 10)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            sample_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Sample corners for background
    bg_samples = []
    for f in sample_frames:
        bg_samples.extend(f[0:30, :].reshape(-1, 3))
        bg_samples.extend(f[-30:, :].reshape(-1, 3))
        bg_samples.extend(f[:, 0:30].reshape(-1, 3))
        bg_samples.extend(f[:, -30:].reshape(-1, 3))
    
    bg_samples = np.array(bg_samples)
    bg_candidates = [tuple((np.round(p / 10) * 10).astype(int)) for p in bg_samples[::10]]
    bg_counts = Counter(bg_candidates)
    most_common_bg = bg_counts.most_common(2)
    
    temp_bg = most_common_bg[0][0]
    if temp_bg == (0, 0, 0) and len(most_common_bg) > 1:
        temp_bg = most_common_bg[1][0]
    
    bg_color = np.clip(np.array(temp_bg), 0, 255).astype(int).tolist()
    print(f"Detected Background Color: {bg_color}")

    # 2. Extract Character Palette using K-Means
    obj_pixels = []
    bg_color_arr = np.array(bg_color)
    
    for f in sample_frames:
        diff = np.linalg.norm(f.astype(float) - bg_color_arr, axis=2)
        mask = diff > 60
        center_mask = np.zeros_like(mask)
        h, w = mask.shape
        center_mask[h//4:3*h//4, w//4:3*w//4] = 1
        effective_mask = mask & center_mask
        pixels = f[effective_mask]
        if len(pixels) > 0:
            obj_pixels.extend(pixels[::50])

    if not obj_pixels:
        print("Warning: No object pixels detected!")
        palette = [[128, 128, 128], [0, 0, 0]]
    else:
        print(f"Clustering {len(obj_pixels)} pixels for palette...")
        kmeans = KMeans(n_clusters=min(12, len(obj_pixels)), n_init=10)
        kmeans.fit(obj_pixels)
        palette = kmeans.cluster_centers_.astype(int).tolist()
    
    # Filter palette: remove colors too close to background
    palette = [c for c in palette if np.linalg.norm(np.array(c) - bg_color_arr) > 80]
    
    print("Detected Palette:")
    for color in palette:
        print(f"  {color}")

    # 3. Estimate Voxel Size
    pixels_per_voxel = 10
    voxel_height = 32
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
    ret, frame = cap.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sobelx = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1))
        sobely = np.abs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1))
        
        def get_spacing(grad):
            spacings = []
            for row in grad[::5]:
                indices = np.where(row > 40)[0]
                if len(indices) > 1:
                    spacings.extend(np.diff(indices))
            if not spacings: return 10
            counts = Counter([s for s in spacings if 3 < s < 40])
            if not counts: return 10
            return max(counts, key=counts.get)

        # Override: User specified target height of ~70 voxels
        # We calculate pixels_per_voxel based on median pixel height
        
        # Estimate Height (Robust)
        heights = []
        for i in range(0, total_frames, 10):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, f = cap.read()
            if not ret: continue
            
            f_rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            diff = np.linalg.norm(f_rgb.astype(float) - bg_color_arr, axis=2)
            mask = diff > 60
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel).astype(bool)
            rows = np.any(mask, axis=1)
            if np.any(rows):
                indices = np.where(rows)[0]
                h = indices[-1] - indices[0]
                heights.append(h)
        
        if heights:
            pixel_height = int(np.median(heights))
            target_voxel_height = 70
            pixels_per_voxel = max(1, int(pixel_height / target_voxel_height))
            
            print(f"User Override: Target Height ~{target_voxel_height} voxels.")
            print(f"Detected Pixel Height: {pixel_height}px -> {pixels_per_voxel} px/voxel")
            
            voxel_height = int(pixel_height / pixels_per_voxel)
        else:
            print("Warning: Could not detect object height.")
            pixels_per_voxel = 10
            voxel_height = 70

    metadata = {
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": total_frames,
        "background_color": bg_color,
        "palette": palette,
        "pixels_per_voxel": pixels_per_voxel,
        "voxel_height": voxel_height
    }

    with open(output_json, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {output_json}")

if __name__ == "__main__":
    analyze_video("voxel_character.mp4")
