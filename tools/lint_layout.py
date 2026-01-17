import json
import os
import math
import sys

# Add root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from primitives import volumes

def rotate_point(x, y, angle_deg):
    """Rotates a 2D point around (0,0) in 90-degree increments."""
    angle_deg = angle_deg % 360
    if angle_deg == 0: return x, y
    if angle_deg == 90: return -y, x
    if angle_deg == 180: return -x, -y
    if angle_deg == 270: return y, -x
    
    # Fallback for non-90 (though we should stick to 90s for voxels)
    rad = math.radians(angle_deg)
    return (x * math.cos(rad) - y * math.sin(rad), 
            x * math.sin(rad) + y * math.cos(rad))

def load_layout_flattened(layout_path, parent_pos=(0,0,0), parent_rot=0):
    if not os.path.exists(layout_path): return []
    with open(layout_path, 'r') as f:
        data = json.load(f)
    
    # Handle dict input (scene format) vs list input (legacy)
    items = []
    if isinstance(data, dict):
        items = data.get('layout', [])
    else:
        items = data

    flat = []
    local_instances = {}
    
    for item in items:
        aid = item['asset_id']
        
        # 1. Resolve Transform
        if 'snap_to' in item:
            target_id, point_name = item['snap_to'].split('.')
            if target_id not in local_instances: continue
            t_info = local_instances[target_id]
            
            # Load target asset for snap point
            t_path = os.path.join("csg", f"{t_info['asset_id']}.json")
            if not os.path.exists(t_path): continue
            with open(t_path, 'r') as tf:
                t_data = json.load(tf)
                if 'snap_points' not in t_data or point_name not in t_data['snap_points']: continue
                s_def = t_data['snap_points'][point_name]
            
            rx, ry = rotate_point(s_def['pos'][0], s_def['pos'][1], t_info['rot'])
            gx, gy, gz = t_info['pos'][0] + rx, t_info['pos'][1] + ry, t_info['pos'][2] + s_def['pos'][2]
            gr = (t_info['rot'] + s_def.get('rot', 0)) % 360
        else:
            lx, ly, lz = item.get('pos', [0,0,0])
            rx, ry = rotate_point(lx, ly, parent_rot)
            gx, gy, gz = parent_pos[0] + rx, parent_pos[1] + ry, parent_pos[2] + lz
            gr = (item.get('rot', 0) + parent_rot) % 360

        if 'id' in item:
            local_instances[item['id']] = {'pos': (gx, gy, gz), 'rot': gr, 'asset_id': aid}

        # 2. Check if Collection or Asset
        path = os.path.join("csg", f"{aid}.json")
        is_col = False
        if os.path.exists(path):
            with open(path, 'r') as cf:
                c_data = json.load(cf)
                if isinstance(c_data, list):
                    is_col = True
                elif isinstance(c_data, dict) and 'layout' in c_data:
                    is_col = True
        
        if is_col:
            flat.extend(load_layout_flattened(path, (gx, gy, gz), gr))
        else:
            flat.append({'asset_id': aid, 'pos': (gx, gy, gz), 'rot': gr})
            
    return flat

CACHE_VOXELS = {}

def get_asset_voxels(asset_id):
    if asset_id in CACHE_VOXELS:
        return CACHE_VOXELS[asset_id]

    path = os.path.join("csg", f"{asset_id}.json")
    if not os.path.exists(path): return set()
    with open(path, 'r') as f:
        data = json.load(f)
    
    voxels = set()
    for op in data.get("instructions", []):
        shape = op.get("shape", "cuboid")
        pos = op.get("pos", [0,0,0])
        coords = []
        if shape == "cuboid":
            size = op.get("size", [1,1,1])
            coords = volumes.get_cuboid_voxels(pos[0], pos[1], pos[2], size[0], size[1], size[2])
        elif shape == "point_cloud":
            coords = [(p[0] + pos[0], p[1] + pos[1], p[2] + pos[2]) for p in op.get("points", [])]
        
        if op['op'] == "add": voxels.update(coords)
        elif op['op'] == "subtract": voxels.difference_update(coords)
        # intersect not implemented for speed in linter
    
    CACHE_VOXELS[asset_id] = voxels
    return voxels

def check_unit_grounding(layout_file):
    print("\nChecking Unit Grounding...")
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    units = []
    if isinstance(data, dict):
        # Extract units from teams, assuming simple list of [x,y,z]
        for u in data.get('team1_units', []): units.append({'pos': u, 'team': 'Team 1'})
        for u in data.get('team2_units', []): units.append({'pos': u, 'team': 'Team 2'})
    
    if not units:
        print("  No units found to check.")
        return

    # Build Sparse Floor Heightmap
    items = load_layout_flattened(layout_file)
    floor_heights = {} # (x, y) -> max_z

    print("  Building floor heightmap...")
    for item in items:
        if is_floor_asset(item['asset_id']):
            local_voxels = get_asset_voxels(item['asset_id'])
            for vx, vy, vz in local_voxels:
                # Transform to world space
                rx, ry = rotate_point(vx, vy, item['rot'])
                wx, wy = int(item['pos'][0] + rx), int(item['pos'][1] + ry)
                wz = int(item['pos'][2] + vz)
                
                # We want the TOP surface, so Z+1 is where the unit stands
                surface_z = wz + 1 
                
                if (wx, wy) not in floor_heights or surface_z > floor_heights[(wx, wy)]:
                    floor_heights[(wx, wy)] = surface_z

    # Check Units
    errors = 0
    for u in units:
        # Units are usually float coordinates, snap to nearest integer voxel column
        ux, uy, uz = int(round(u['pos'][0])), int(round(u['pos'][1])), int(u['pos'][2])
        
        if (ux, uy) in floor_heights:
            floor_z = floor_heights[(ux, uy)]
            # Tolerance of 1 voxel?
            if abs(uz - floor_z) > 1:
                print(f"  ERROR: {u['team']} Unit at ({ux}, {uy}, {uz}) is not on floor (Floor Z: {floor_z})")
                errors += 1
        else:
             print(f"  ERROR: {u['team']} Unit at ({ux}, {uy}, {uz}) is floating (No floor detected below)")
             errors += 1
             
    if errors == 0:
        print("  SUCCESS: All characters are firmly grounded.")

CACHE_METADATA = {}

def get_asset_tags(asset_id):
    if asset_id in CACHE_METADATA:
        return CACHE_METADATA[asset_id].get('tags', [])

    path = os.path.join("csg", f"{asset_id}.json")
    if not os.path.exists(path): return []
    with open(path, 'r') as f:
        data = json.load(f)
    
    CACHE_METADATA[asset_id] = data
    return data.get('tags', [])

def is_floor_asset(asset_id):
    tags = get_asset_tags(asset_id)
    return 'floor' in tags

def check_unit_occlusion(layout_file):
    print("\nChecking Unit Occlusion...")
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    units = []
    if isinstance(data, dict):
        for u in data.get('team1_units', []): units.append({'pos': u, 'team': 'Team 1'})
        for u in data.get('team2_units', []): units.append({'pos': u, 'team': 'Team 2'})
    
    if not units: return
    
    items = load_layout_flattened(layout_file)
    
    # Unit dimensions
    u_rad = 4
    u_height = 32
    
    errors = 0
    
    for u in units:
        ux, uy, uz = u['pos'][0], u['pos'][1], u['pos'][2]
        
        collision_found = False
        
        for item in items:
            tags = get_asset_tags(item['asset_id'])
            
            # Optimization: Only check confirmed occluders
            if 'occluder' not in tags: continue
            
            # Use previously cached voxels logic...
            local_voxels = get_asset_voxels(item['asset_id'])
            for vx, vy, vz in local_voxels:
                # Transform to world
                rx, ry = rotate_point(vx, vy, item['rot'])
                wx, wy = item['pos'][0] + rx, item['pos'][1] + ry
                wz = item['pos'][2] + vz
                
                # Check intersection with Unit Cylinder
                if (wx - ux)**2 + (wy - uy)**2 < u_rad**2:
                    if uz <= wz < uz + u_height:
                        print(f"  ERROR: {u['team']} Unit at ({ux}, {uy}, {uz}) is stuck inside '{item['asset_id']}' at ({wx}, {wy}, {wz})")
                        errors += 1
                        collision_found = True
                        break 
            
            if collision_found: break

    if errors == 0:
        print("  SUCCESS: All spawn points are clear of obstacles.")

def check_team_distance(layout_file):
    print("\nChecking Team Engagement Distance...")
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, dict) or 'team1_units' not in data or 'team2_units' not in data:
        print("  Skipping distance check (Teams not defined in scene).")
        return

    t1 = data['team1_units']
    t2 = data['team2_units']
    
    if not t1 or not t2: return

    # Calculate Centroids
    c1 = [sum(x)/len(t1) for x in zip(*t1)]
    c2 = [sum(x)/len(t2) for x in zip(*t2)]
    
    # Euclidean Distance
    dist = math.sqrt(sum((a - b)**2 for a, b in zip(c1, c2)))
    
    print(f"  Centroid Team 1: ({c1[0]:.1f}, {c1[1]:.1f}, {c1[2]:.1f})")
    print(f"  Centroid Team 2: ({c2[0]:.1f}, {c2[1]:.1f}, {c2[2]:.1f})")
    print(f"  Engagement Distance: {dist:.1f} voxels")
    
    if 100 <= dist <= 200:
        print("  SUCCESS: Teams are correctly spaced for combat (100-200 range).")
    elif dist < 100:
        print(f"  ERROR: Teams are TOO CLOSE ({dist:.1f} < 100). Move them further apart.")
    else:
        print(f"  ERROR: Teams are TOO FAR ({dist:.1f} > 200). Move them closer.")

def check_camera_focus(layout_file):
    print("\nChecking Camera Focus...")
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, dict): return
    if 'team1_units' not in data or 'team2_units' not in data or 'camera' not in data:
        print("  Skipping camera check (Missing metadata).")
        return

    t1 = data['team1_units']
    t2 = data['team2_units']
    cam = data['camera']
    
    if not t1 or not t2: return

    # Calculate Midpoint of Teams
    c1 = [sum(x)/len(t1) for x in zip(*t1)]
    c2 = [sum(x)/len(t2) for x in zip(*t2)]
    midpoint = [(a+b)/2 for a, b in zip(c1, c2)]
    
    # Camera Center
    cc = cam.get('center', [0,0,0])
    
    # Distance
    dist = math.sqrt((midpoint[0]-cc[0])**2 + (midpoint[1]-cc[1])**2) # 2D Check (XY)
    
    print(f"  Team Midpoint: ({midpoint[0]:.1f}, {midpoint[1]:.1f})")
    print(f"  Camera Center: ({cc[0]:.1f}, {cc[1]:.1f})")
    print(f"  Focus Error: {dist:.1f} voxels")
    
    if dist <= 100:
        print("  SUCCESS: Camera is focused near the action.")
    else:
        print(f"  ERROR: Camera is too far from unit midpoint ({dist:.1f} > 100). Re-center it.")

def ray_box_intersection(ray_origin, ray_dir, box_min, box_max):
    """Slab method for ray-box intersection."""
    t_min = float('-inf')
    t_max = float('inf')

    for i in range(3):
        if abs(ray_dir[i]) < 1e-6:
            if ray_origin[i] < box_min[i] or ray_origin[i] > box_max[i]:
                return False
        else:
            inv_d = 1.0 / ray_dir[i]
            t1 = (box_min[i] - ray_origin[i]) * inv_d
            t2 = (box_max[i] - ray_origin[i]) * inv_d
            t_min = max(t_min, min(t1, t2))
            t_max = min(t_max, max(t1, t2))

    return t_max >= max(0.0, t_min)

def check_camera_line_of_sight(layout_file):
    print("\nChecking Camera Line of Sight...")
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, dict): return
    if 'team1_units' not in data or 'team2_units' not in data or 'camera' not in data: return

    units = []
    for u in data['team1_units']: units.append(u)
    for u in data['team2_units']: units.append(u)
    
    cam_pos = data['camera'].get('eye', [0,0,0])
    
    items = load_layout_flattened(layout_file)
    
    # Pre-calculate asset bounding boxes for speed
    # We'll use a rough heuristic: scan voxels once to get min/max
    asset_bboxes = {}
    
    for item in items:
        tags = get_asset_tags(item['asset_id'])
        if 'occluder' not in tags: continue
        
        # Skip small occluders (tables, chairs) that don't block full view?
        # Maybe check height? If max_z < 20, ignore?
        # Let's get bbox first.
        
        local_voxels = get_asset_voxels(item['asset_id'])
        if not local_voxels: continue
        
        # Transform all to world? Expensive.
        # Faster: Transform local bbox? No, rotation.
        # We must transform voxels to get world bbox.
        
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
        
        for vx, vy, vz in local_voxels:
            rx, ry = rotate_point(vx, vy, item['rot'])
            wx, wy = item['pos'][0] + rx, item['pos'][1] + ry
            wz = item['pos'][2] + vz
            
            min_x = min(min_x, wx); max_x = max(max_x, wx)
            min_y = min(min_y, wy); max_y = max(max_y, wy)
            min_z = min(min_z, wz); max_z = max(max_z, wz)
            
        # Ignore short obstacles (furniture)
        if max_z < 30: continue
            
        asset_bboxes[item['asset_id'] + str(item['pos'])] = (
            [min_x, min_y, min_z], [max_x, max_y, max_z], item['asset_id']
        )

    blocked_count = 0
    for u in units:
        # Target head level (Z+15)
        target = [u[0], u[1], u[2] + 15]
        
        # Ray Direction
        ray_vec = [target[0] - cam_pos[0], target[1] - cam_pos[1], target[2] - cam_pos[2]]
        ray_len = math.sqrt(sum(x*x for x in ray_vec))
        ray_dir = [x / ray_len for x in ray_vec]
        
        for key, (b_min, b_max, aid) in asset_bboxes.items():
            # Shrink box slightly to avoid self-intersection or grazing
            b_min_s = [x + 1 for x in b_min]
            b_max_s = [x - 1 for x in b_max]
            
            if ray_box_intersection(cam_pos, ray_dir, b_min_s, b_max_s):
                # Check distance (must be closer than unit)
                # Simple midpoint check? Or exact t check?
                # ray_box returns bool. We need t.
                # Assuming standard rendering, if it intersects, it blocks.
                # BUT unit is BEHIND it.
                # Distance to box center
                box_center = [(b_min[i] + b_max[i])/2 for i in range(3)]
                dist_box = math.sqrt(sum((box_center[i] - cam_pos[i])**2 for i in range(3)))
                
                if dist_box < ray_len - 10: # 10 unit buffer
                    print(f"  ERROR: View to unit at {u} is blocked by '{aid}'")
                    blocked_count += 1
                    break

    if blocked_count == 0:
        print("  SUCCESS: Camera has clear line of sight to all units.")

def lint_layout(layout_file):
    print(f"Linting: {layout_file}")
    items = load_layout_flattened(layout_file)
    print(f"  Found {len(items)} leaf assets.")
    
    global_map = {} # (x,y,z) -> asset_index
    collisions = [] # list of (idx1, idx2, count)
    
    for i, item in enumerate(items):
        aid = item['asset_id']
        local_voxels = get_asset_voxels(aid)
        
        # Transform to world space
        for vx, vy, vz in local_voxels:
            rx, ry = rotate_point(vx, vy, item['rot'])
            wx, wy, wz = int(item['pos'][0] + rx), int(item['pos'][1] + ry), int(item['pos'][2] + vz)
            
            coord = (wx, wy, wz)
            if coord in global_map:
                other_idx = global_map[coord]
                if other_idx != i:
                    collisions.append((other_idx, i, coord))
            else:
                global_map[coord] = i
                
    if not collisions:
        print("  CLEAN! No voxel collisions detected.")
    else:
        # Group collisions by asset pairs
        pairs = {}
        for c in collisions:
            pair = tuple(sorted((c[0], c[1])))
            pairs[pair] = pairs.get(pair, 0) + 1
            
        print(f"  ERROR: Found {len(collisions)} overlapping voxels between {len(pairs)} asset pairs:")
        # Limit output for sanity
        count = 0
        for (i1, i2), c_count in pairs.items():
            if count >= 10: 
                print(f"    ... and {len(pairs) - 10} more pairs.")
                break
            a1, a2 = items[i1], items[i2]
            print(f"    - {a1['asset_id']} and {a2['asset_id']} overlap by {c_count} voxels.")
            count += 1
            
    # Run Grounding Check
    check_unit_grounding(layout_file)
    # Run Occlusion Check
    check_unit_occlusion(layout_file)
    # Run Distance Check
    check_team_distance(layout_file)
    # Run Camera Check
    check_camera_focus(layout_file)
    # Run LoS Check
    check_camera_line_of_sight(layout_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/lint_layout.py csg/layout.json")
    else:
        lint_layout(sys.argv[1])
