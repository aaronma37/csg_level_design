import cv2
import numpy as np
import json
import math
import sys
import os
import random
import time

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
        
        voxels = {} # (x,y,z) -> color_index
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
                        raw_voxels.append((x,y,z,c))
                        
                elif chunk_id == b'RGBA':
                    for i in range(256):
                        r = content[i*4]
                        g = content[i*4+1]
                        b = content[i*4+2]
                        a = content[i*4+3]
                        palette.append((r,g,b,a))
                        
            except Exception as e:
                print(f"Error parsing VOX: {e}")
                break
    
    # APPLY EXACT OFFSETS (From Phase 2 Output)
    # Printed: SAVE_OFFSET: -12 -24 -18
    # min_x (-12) = Grid X min
    # min_y (-24) = Grid Y min
    # min_z (-18) = Grid Z min
    
    # Mapping logic determined:
    # Grid X = File X + (-12)
    # Grid Y = File Z + (-24)  (Note: File Z comes from Grid Y)
    # Grid Z = File Y + (-18)  (Note: File Y comes from Grid Z)
    
    off_x = -12
    off_y = -25 # Updated from latest Phase 2
    off_z = -18
    
    if raw_voxels:
        for x, y, z, c in raw_voxels:
            # x, y, z are from File (0..N)
            
            # Map back to Grid
            gx = x + off_x
            gy = z + off_y # File Z -> Grid Y
            gz = y + off_z # File Y -> Grid Z
            
            # Store in dict as (x,y,z)
            voxels[(gx, gy, gz)] = c
                
    return voxels, palette

def refine(model_path, video_path, metadata_path, output_path="refined_model.vox"):
    print("--- Phase 3: Simulated Annealing Refinement ---")
    
    # 1. Load Data
    with open(metadata_path, 'r') as f:
        meta = json.load(f)
    
    bg_color = np.array(meta["background_color"])
    pixels_per_voxel = meta["pixels_per_voxel"] # Should be 4
    
    # Load Model
    print(f"Loading {model_path}...")
    initial_voxels, raw_palette = load_vox_file(model_path)
    print(f"Loaded {len(initial_voxels)} voxels.")
    
    # Convert palette to lookup
    # Palette is 0-255. Index 1-255.
    # We need a quick way to get RGB from Index
    palette_rgb = {}
    for i, c in enumerate(raw_palette):
        palette_rgb[i+1] = np.array(c[:3])

    # 2. Setup Rays (Subset of Views)
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    total_frames = meta["total_frames"]
    # We use fewer views for annealing speed (e.g., every 8th frame -> ~24 views)
    stride = max(1, total_frames // 24)
    
    print(f"Loading reference frames (stride {stride})...")
    frame_idx = 0
    views = []
    
    cx = meta["width"] / 2
    cy = meta["height"] / 2
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if frame_idx % stride == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            angle = -(frame_idx / total_frames) * 2 * math.pi
            views.append({
                'id': frame_idx,
                'image': frame,
                'angle': angle,
                'sin': math.sin(angle),
                'cos': math.cos(angle)
            })
        frame_idx += 1
    cap.release()
    
    # 3. Build Ray Casting Structure
    # For every pixel in every view, we need a list of voxels it hits.
    # Since iterating pixels is slow, we iterate VOXELS and project them.
    # Map: (ViewID, PixelU, PixelV) -> List of [Depth, VoxelCoords]
    
    print("Building Ray-Voxel map (this may take a moment)...")
    
    # We use a flat dictionary key -> list
    # Key: (view_idx, u, v)
    # Value: list of (depth, (x,y,z))
    # Optimization: Only store rays that hit something.
    
    ray_hits = {} 
    
    # To quickly find which rays a voxel belongs to:
    # Voxel -> List of Keys in ray_hits
    voxel_to_rays = {v: [] for v in initial_voxels}
    
    for (vx, vy, vz) in initial_voxels:
        for v_idx, view in enumerate(views):
            # Project
            rx = vx * view['cos'] - vz * view['sin']
            rz = vx * view['sin'] + vz * view['cos']
            
            # Mirror X
            u = int(-rx * pixels_per_voxel + cx)
            v = int(-vy * pixels_per_voxel + cy)
            
            if 0 <= u < meta["width"] and 0 <= v < meta["height"]:
                key = (v_idx, u, v)
                if key not in ray_hits:
                    ray_hits[key] = []
                
                # We store (depth, coords)
                # We use -rz as depth so that larger is "closer" if camera is at -Z?
                # Actually, in our rotation:
                # Angle 0: x'=x, z'=z. Cam at -Z.
                # Point (0,0,-10) is closer than (0,0,0).
                # So smaller Z is closer.
                depth = rz 
                
                ray_hits[key].append([depth, (vx, vy, vz)])
                voxel_to_rays[(vx, vy, vz)].append(key)

    # Sort all rays by depth (Ascending: Smallest Z is Closest)
    for k in ray_hits:
        ray_hits[k].sort(key=lambda x: x[0])

    print(f"Mapped {len(ray_hits)} active rays.")

    # 4. Annealing State
    current_voxels = set(initial_voxels.keys())
    
    # Calculate Initial Energy
    def get_pixel_error(color_observed, color_rendered):
        # Squared Euclidean distance
        return np.sum((color_observed - color_rendered) ** 2)

    total_energy = 0
    
    # Cache for current visible voxel index in each ray list
    # ray_key -> current_index_in_list
    # If index >= len, it hits background.
    ray_status = {k: 0 for k in ray_hits}
    
    # Helper to get current color of a ray
    def get_ray_color(key):
        idx = ray_status[key]
        hits = ray_hits[key]
        
        # Advance index if current voxel was removed (lazy update? No, we need current state)
        # We assume ray_status is kept up to date.
        
        if idx < len(hits):
            # Check if this voxel still exists? 
            # To avoid checking the set every time, we rely on the annealing loop to update ray_status.
            # But wait, 'hits' contains ALL initial voxels.
            # If we remove a voxel, we don't remove it from 'hits' list (too slow).
            # We just mark it as "removed" in the 'current_voxels' set?
            # Accessing set is O(1).
            
            # Find the first voxel in the list that is in current_voxels
            # Optimization: Update ray_status to point to it.
            while idx < len(hits):
                v_coords = hits[idx][1]
                if v_coords in current_voxels:
                    # Found it
                    ray_status[key] = idx
                    v_idx = initial_voxels[v_coords]
                    if v_idx in palette_rgb:
                         return palette_rgb[v_idx]
                    return np.array([128,128,128]) # Fallback
                idx += 1
            
            # If we fell off the end, update status
            ray_status[key] = idx
            
        return bg_color

    print("Calculating initial energy...")
    for key, hits in ray_hits.items():
        v_idx, u, v = key
        obs_color = views[v_idx]['image'][v, u]
        rend_color = get_ray_color(key)
        total_energy += get_pixel_error(obs_color, rend_color)

    print(f"Initial Energy: {total_energy:,.0f}")
    
    # 5. Annealing Loop
    T = 2000.0 # Hotter start
    alpha = 0.98 # Slower cooling
    iterations = 40000 # More iterations
    
    accepted = 0
    
    # Neighbor offsets for regularization
    neighbors = [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]
    
    start_time = time.time()
    
    # We need a quick lookup for occupancy
    # current_voxels is a set.
    
    for i in range(iterations):
        # Move Type: 0 = Remove, 1 = Add
        # Bias towards removal? Or balanced?
        # If we have holes, we need ADD.
        move_type = random.choice([0, 1])
        
        # PICK TARGET
        if move_type == 0: # REMOVE
            if not current_voxels: continue
            # Sample from current
            # Convert to list is slow every iter. 
            # Optimization: maintain list? Or just sample random?
            # Sample random element from set is O(N) usually.
            # Python set pop/add is O(1).
            # Let's keep a list 'voxel_list' and sync it?
            # For now, just pop and add back if rejected.
            v_coords = current_voxels.pop()
            current_voxels.add(v_coords) # Put it back for now
            
        else: # ADD
            # Pick a neighbor of an existing voxel that is EMPTY
            if not current_voxels: continue
            # Sample random existing
            ref_vox = random.sample(sorted(current_voxels), 1)[0] # Slow?
            # Pick random neighbor
            dx, dy, dz = random.choice(neighbors)
            v_coords = (ref_vox[0]+dx, ref_vox[1]+dy, ref_vox[2]+dz)
            
            if v_coords in current_voxels:
                continue # Already exists
                
            # Bounds check?
            # Optional, but keep it within reasonable grid
            if abs(v_coords[0]) > 64 or abs(v_coords[1]) > 100 or abs(v_coords[2]) > 64:
                continue

        # CALCULATE DELTA E
        delta_E = 0
        
        # 1. PIXEL ERROR TERM
        # If adding: voxel becomes opaque.
        # If removing: voxel becomes transparent.
        
        affected_rays = []
        is_visible = False
        
        if v_coords in voxel_to_rays: # Might be in our pre-calc map
            for key in voxel_to_rays[v_coords]:
                current_hit_idx = ray_status[key]
                hits = ray_hits[key]
                
                # Check if this voxel is RELEVANT for this ray
                # i.e., is it the first hit? Or in front of the first hit?
                
                # Find index of v_coords in hits list (pre-calculated depth sort)
                # This linear scan is the bottleneck.
                # Optimization: 'hits' is small (usually < 200).
                
                my_idx = -1
                for idx, h in enumerate(hits):
                    if h[1] == v_coords:
                        my_idx = idx
                        break
                
                if my_idx == -1: continue # Not in this ray's path
                
                # CASE: REMOVE
                if move_type == 0:
                    if my_idx == current_hit_idx: # We are the visible surface
                        is_visible = True
                        
                        v_idx, u, v = key
                        obs = views[v_idx]['image'][v, u]
                        
                        # Current: Color of V
                        v_col_idx = initial_voxels.get(v_coords, 1) # Fallback idx
                        curr_col = palette_rgb.get(v_col_idx, bg_color)
                        
                        # Next: Color of voxel behind
                        next_col = bg_color
                        next_valid_idx = my_idx + 1
                        while next_valid_idx < len(hits):
                            if hits[next_valid_idx][1] in current_voxels:
                                nid = initial_voxels.get(hits[next_valid_idx][1], 1)
                                next_col = palette_rgb.get(nid, bg_color)
                                break
                            next_valid_idx += 1
                        
                        curr_err = get_pixel_error(obs, curr_col)
                        new_err = get_pixel_error(obs, next_col)
                        delta_E += (new_err - curr_err)
                        affected_rays.append((key, next_valid_idx))

                # CASE: ADD
                else: # move_type == 1
                    # If we add V, does it occlude the current surface?
                    # Only if my_idx < current_hit_idx
                    
                    if my_idx <= current_hit_idx: # We are in front (or same slot if empty)
                        # We become the new surface
                        v_idx, u, v = key
                        obs = views[v_idx]['image'][v, u]
                        
                        # Current Surface Color
                        # (Need to fetch what is currently visible)
                        # We rely on ray_status pointing to current valid surface
                        # But wait, if ray_status points to index 10, and we are index 5 (closer), we block it.
                        
                        # Find current visible color
                        curr_visible_idx = current_hit_idx
                        curr_col = bg_color
                        # Ensure current_hit_idx is valid (points to existing voxel)
                        # The loop logic updates ray_status, so it should be valid.
                        if curr_visible_idx < len(hits):
                             # Double check it exists (it should)
                             cid = initial_voxels.get(hits[curr_visible_idx][1], 1)
                             curr_col = palette_rgb.get(cid, bg_color)
                        
                        # New Color (Us)
                        # What color do we have?
                        # We don't have a color yet! It's a new voxel.
                        # Heuristic: Inherit color from nearest neighbor or use average palette?
                        # Or check which palette color minimizes error?
                        # Let's try to pick the BEST color for this view.
                        # Simplified: Use neighbor color.
                        # Identify nearest neighbor
                        nn_color = (128,128,128)
                        for n in neighbors:
                            nb = (v_coords[0]+n[0], v_coords[1]+n[1], v_coords[2]+n[2])
                            if nb in initial_voxels: # Use initial data for color lookup
                                nn_color = palette_rgb.get(initial_voxels[nb], nn_color)
                                break
                        
                        # Or better: Pick color that minimizes error against observation?
                        # That's cheating/optimizing.
                        # Let's use the nearest neighbor color from initial model.
                        # If we are adding a voxel that was never in initial model, we don't have color.
                        # Fallback: We can only add voxels that were in the initial "Hull" but removed?
                        # No, we want to fill holes.
                        # Let's assume we can only toggle voxels present in 'initial_voxels' set (The Visual Hull).
                        # This simplifies everything. We are just toggling visibility of the Hull.
                        # 'reconstructed_model.vox' IS the Hull.
                        
                        if v_coords in initial_voxels:
                             vid = initial_voxels[v_coords]
                             my_col = palette_rgb.get(vid, bg_color)
                             
                             curr_err = get_pixel_error(obs, curr_col)
                             new_err = get_pixel_error(obs, my_col)
                             delta_E += (new_err - curr_err)
                             affected_rays.append((key, my_idx))
                        else:
                             # Can't add voxel outside visual hull (no color data)
                             delta_E += 999999 # Forbidden

        # 2. REGULARIZATION TERM (Smoothness)
        # Count neighbors
        nb_count = 0
        for n in neighbors:
             nb = (v_coords[0]+n[0], v_coords[1]+n[1], v_coords[2]+n[2])
             if nb in current_voxels:
                 nb_count += 1
        
        # Energy penalty for having few neighbors (Isolated)
        # We want to maximize neighbors.
        # Energy = -Weight * Neighbors
        
        reg_weight = 200.0 # Heuristic weight
        
        # If removing: Neighbors decrease by 1 for my neighbors? 
        # Easier: Compare state before and after.
        # State Before: voxel present (if removing). Neighbors = nb_count.
        # State After: voxel absent. Neighbors = 0 (for this voxel).
        # Change in Energy:
        # If Removing: We go from High Neighbor Count (Low Energy) to 0. Energy INCREASES.
        # Delta Reg = (Energy_After - Energy_Before)
        #           = (0 - (-W * nb_count)) = W * nb_count
        # Removing a connected voxel costs Energy. (Discourages making holes).
        
        # If Adding: We go from 0 to nb_count.
        # Delta Reg = (-W * nb_count - 0) = -W * nb_count.
        # Adding a connected voxel reduces Energy. (Encourages filling holes).
        
        if move_type == 0: # Remove
            delta_E += reg_weight * nb_count
        else: # Add
            delta_E -= reg_weight * nb_count

        # 3. METROPOLIS UPDATE
        if delta_E < 0 or random.random() < math.exp(-delta_E / T):
            if move_type == 0:
                current_voxels.remove(v_coords)
                # Update rays
                for key, new_idx in affected_rays:
                    ray_status[key] = new_idx
            else:
                current_voxels.add(v_coords)
                # Update rays
                for key, new_idx in affected_rays:
                    ray_status[key] = new_idx
            
            total_energy += delta_E
            accepted += 1
        
        # Cooling
        if i % 2000 == 0:
            T *= alpha
            print(f"Iter {i}: Energy {total_energy:,.0f} | Temp {T:.1f} | Voxels {len(current_voxels)} | Acc {accepted}")
            accepted = 0

    print(f"Final Energy: {total_energy:,.0f}")
    
    # 6. Save
    print("Saving refined model...")
    # Reconstruct VoxelModel for saving
    final_model = VoxelModel()
    
    # Copy palette
    final_model.palette = [(0,0,0,0)] * 256 # Reset
    for i, c in enumerate(raw_palette):
        if i < 255:
            final_model.palette[i+1] = c
            
    # Add Voxels
    print("Mapping colors for final model...")
    for (x,y,z) in current_voxels:
        if (x,y,z) in initial_voxels:
            c_idx = initial_voxels[(x,y,z)]
        else:
            # New voxel! Find nearest neighbor in initial_voxels to inherit color
            # Heuristic: Spiral out to find color
            found_color_idx = 1 # Default
            min_dist = 999
            
            # Check immediate neighbors first
            for n in neighbors:
                nb = (x+n[0], y+n[1], z+n[2])
                if nb in initial_voxels:
                    found_color_idx = initial_voxels[nb]
                    break
            
            c_idx = found_color_idx
            
        final_model.voxels[(x,z,y)] = c_idx

    final_model.save(output_path)
    print("Done.")

if __name__ == "__main__":
    refine("reconstructed_model.vox", "voxel_character.mp4", "video_metadata.json")
