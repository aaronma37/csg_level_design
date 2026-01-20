import os
import re
import json
import math

# Path configuration
TILES_DIR = "csg_assets/tiles"
CSG_DIR = "csg"
GAME_TILES_DIR = os.path.expanduser("~/love_exp/assets/csg_assets/tiles")

def rotate_point(x, y, angle_deg):
    if angle_deg == 0: return x, y
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    # Standard rotation (Counter-Clockwise)
    # (x, y) -> (x cos - y sin, x sin + y cos)
    # MagicaVoxel rotations are sometimes weird, but let's assume standard 2D Z-rot for now.
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    return new_x, new_y

def load_asset_snaps(asset_id):
    # Try finding the json file
    paths = [
        os.path.join(CSG_DIR, f"{asset_id}.json"),
        os.path.join("generators", f"{asset_id}.json") # fallback
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                    return data.get("snap_points", {})
            except:
                pass
    return {}

def parse_lua_table(content):
    # Very basic regex parser for the Lua layout table items
    # Expects format like: { asset_id = '...', ... }
    # This is fragile but avoids a full Lua parser dependency
    items = []
    
    # Find the layout block
    layout_match = re.search(r'layout\s*=\s*\{(.*)\}', content, re.DOTALL)
    if not layout_match:
        return []
    
    layout_str = layout_match.group(1)
    
    # Split by },
    # This assumes consistent formatting
    raw_items = layout_str.split('},')
    
    for raw in raw_items:
        clean = raw.strip().strip('{').strip()
        if not clean: continue
        
        item = {}
        
        # Parse fields
        # asset_id = '...'
        aid_m = re.search(r"asset_id\s*=\s*['\"]([^'\"]+)['\"]", clean)
        if aid_m: 
            item['asset_id'] = aid_m.group(1)
        else:
            # Only warn if it looks like a real item (not just closing braces)
            if len(clean) > 10 and "asset_id" in clean:
                print(f"Warning: Could not find asset_id in item: {clean[:20]}...")
            continue
        
        # id = '...'
        id_m = re.search(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", clean)
        if id_m: item['id'] = id_m.group(1)
        
        # pos = {x, y, z}
        pos_m = re.search(r"pos\s*=\s*\{([^}]+)\}", clean)
        if pos_m:
            vals = [float(x) for x in pos_m.group(1).split(',')]
            while len(vals) < 3: vals.append(0.0)
            item['pos'] = vals
        else:
            item['pos'] = [0.0, 0.0, 0.0] # Default
            
        # rot = n
        rot_m = re.search(r"rot\s*=\s*(-?\d+)", clean)
        if rot_m: item['rot'] = int(rot_m.group(1))
        else: item['rot'] = 0
        
        # snap_to = '...'
        snap_to_m = re.search(r"snap_to\s*=\s*['\"]([^'\"]+)['\"]", clean)
        if snap_to_m: item['snap_to'] = snap_to_m.group(1)
        
        # snap_from = '...'
        snap_from_m = re.search(r"snap_from\s*=\s*['\"]([^'\"]+)['\"]", clean)
        if snap_from_m: item['snap_from'] = snap_from_m.group(1)
        
        items.append(item)
        
    return items

def compile_tile(filename):
    with open(os.path.join(TILES_DIR, filename), 'r') as f:
        content = f.read()
        
    # We need to reconstruct the Lua file with resolved positions
    # 1. Parse Layout
    items = parse_lua_table(content)
    
    # 2. Resolve Snaps
    lookup = {} # id -> item with resolved pos
    
    # Pass 1: Register items with explicit pos (or defaults)
    for item in items:
        if 'id' in item:
            lookup[item['id']] = item
            
    # Pass 2: Resolve snaps
    # (Simple single-pass for now, assumes target is already resolved or earlier in list)
    resolved_layout_str = "    layout = {\n"
    
    for item in items:
        # Resolve Position
        final_pos = list(item['pos'])
        
        if 'snap_to' in item:
            target_id, target_point = item['snap_to'].split('.')
            target_item = lookup.get(target_id)
            
            if target_item:
                # Get Target Snap Point
                t_snaps = load_asset_snaps(target_item['asset_id'])
                t_snap_def = t_snaps.get(target_point)
                
                if t_snap_def:
                    tx, ty, tz = t_snap_def['pos']
                    # Rotate target snap offset by target rotation
                    rtx, rty = rotate_point(tx, ty, target_item['rot'])
                    
                    # Target Global Pos
                    tgx = target_item['pos'][0] + rtx
                    tgy = target_item['pos'][1] + rty
                    tgz = target_item['pos'][2] + tz
                    
                    final_pos = [tgx, tgy, tgz]
                    
                    # Handle snap_from (Offset)
                    if 'snap_from' in item:
                        s_point = item['snap_from']
                        s_snaps = load_asset_snaps(item['asset_id'])
                        s_snap_def = s_snaps.get(s_point)
                        
                        if s_snap_def:
                            sx, sy, sz = s_snap_def['pos']
                            # Rotate source snap offset by CURRENT item rotation
                            rsx, rsy = rotate_point(sx, sy, item['rot'])
                            
                            final_pos[0] -= rsx
                            final_pos[1] -= rsy
                            final_pos[2] -= sz
                            
            # Update item pos for future lookups
            item['pos'] = final_pos
            if 'id' in item:
                lookup[item['id']] = item

        # Write to Lua string
        # Reconstruct the line
        line = f"        {{ asset_id = '{item['asset_id']}', pos = {{{final_pos[0]}, {final_pos[1]}, {final_pos[2]}}}, rot = {item['rot']}"
        if 'id' in item:
            line = f"        {{ id = '{item['id']}', asset_id = '{item['asset_id']}', pos = {{{final_pos[0]}, {final_pos[1]}, {final_pos[2]}}}, rot = {item['rot']}"
        
        # Copy other metadata? (Simplification: Just write basics)
        line += " },\n"
        resolved_layout_str += line

    resolved_layout_str += "    }"
    
    # Replace the layout block safely
    # Assumes layout is the last element in the return table
    match_start = re.search(r'layout\s*=\s*\{', content)
    if match_start:
        new_content = content[:match_start.start()] + resolved_layout_str + "\n}"
    else:
        # Fallback if layout not found (shouldn't happen given parse succeeded)
        print(f"Error: Layout block not found for replacement in {filename}")
        new_content = content
    
    # Write to Game Directory
    os.makedirs(GAME_TILES_DIR, exist_ok=True)
    out_path = os.path.join(GAME_TILES_DIR, filename)
    with open(out_path, 'w') as f:
        f.write(new_content)
    print(f"Compiled {filename} -> {out_path}")

if __name__ == "__main__":
    for f in os.listdir(TILES_DIR):
        if f.endswith(".lua"):
            compile_tile(f)
