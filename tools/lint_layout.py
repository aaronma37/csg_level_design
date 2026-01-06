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
    
    flat = []
    local_instances = {}
    
    for item in data:
        aid = item['asset_id']
        
        # 1. Resolve Transform
        if 'snap_to' in item:
            target_id, point_name = item['snap_to'].split('.')
            t_info = local_instances[target_id]
            
            # Load target asset for snap point
            t_path = os.path.join("csg", f"{t_info['asset_id']}.json")
            with open(t_path, 'r') as tf:
                t_data = json.load(tf)
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
                if isinstance(c_data, list): is_col = True
        
        if is_col:
            flat.extend(load_layout_flattened(path, (gx, gy, gz), gr))
        else:
            flat.append({'asset_id': aid, 'pos': (gx, gy, gz), 'rot': gr})
            
    return flat

def get_asset_voxels(asset_id):
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
    return voxels

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
        for (i1, i2), count in pairs.items():
            a1, a2 = items[i1], items[i2]
            print(f"    - {a1['asset_id']} and {a2['asset_id']} overlap by {count} voxels.")
            print(f"      Locations: {a1['pos']} and {a2['pos']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/lint_layout.py csg/layout.json")
    else:
        lint_layout(sys.argv[1])
