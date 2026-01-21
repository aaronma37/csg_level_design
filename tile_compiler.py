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

def load_asset_data(asset_id):
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
                    return data
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

def parse_manual_lights(content):
    # Parses existing lights table
    lights = []
    match = re.search(r'lights\s*=\s*\{(.*)\}', content, re.DOTALL)
    if not match:
        return lights
        
    raw_str = match.group(1)
    # Dirty regex parse for Lua table entries
    # { position = {32, 25, 32}, color = {1.0, 0.8, 0.4}, intensity = 50 }
    entries = raw_str.split('},')
    for entry in entries:
        if 'position' not in entry: continue
        l = {}
        pos_m = re.search(r"position\s*=\s*\{([^}]+)\}", entry)
        if pos_m: l['position'] = [float(x) for x in pos_m.group(1).split(',')]
        
        col_m = re.search(r"color\s*=\s*\{([^}]+)\}", entry)
        if col_m: l['color'] = [float(x) for x in col_m.group(1).split(',')]
        
        int_m = re.search(r"intensity\s*=\s*([\d\.]+)", entry)
        if int_m: l['intensity'] = float(int_m.group(1))
        
        if 'position' in l:
            lights.append(l)
    return lights

def compile_tile(filename):
    with open(os.path.join(TILES_DIR, filename), 'r') as f:
        content = f.read()
        
    # We need to reconstruct the Lua file with resolved positions
    # 1. Parse Layout
    items = parse_lua_table(content)
    
    # 2. Parse Manual Lights
    final_lights = parse_manual_lights(content)
    
    # 3. Resolve Snaps & Collect Auto-Lights
    lookup = {} # id -> item with resolved pos
    
    # Pass 1: Register items with explicit pos (or defaults)
    for item in items:
        if 'id' in item: lookup[item['id']] = item
        if 'asset_id' in item and item['asset_id'] not in lookup:
            lookup[item['asset_id']] = item
            
    # Pass 2: Resolve snaps & lights
    resolved_layout_str = "    layout = {\n"
    
    for item in items:
        asset_data = load_asset_data(item['asset_id'])
        snap_points = asset_data.get("snap_points", {})
        
        # Resolve Position
        final_pos = list(item['pos'])
        
        if 'snap_to' in item:
            if '.' in item['snap_to']:
                target_id, target_point = item['snap_to'].split('.')
                target_item = lookup.get(target_id)
                
                if target_item:
                    # Need to load target's asset data to find its snap points
                    target_asset_data = load_asset_data(target_item['asset_id'])
                    t_snaps = target_asset_data.get("snap_points", {})
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
                            s_snap_def = snap_points.get(s_point)
                            
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

        # --- AUTO LIGHTING ---
        if 'light_emitters' in asset_data:
            for emitter in asset_data['light_emitters']:
                ex, ey, ez = emitter['offset']
                
                # Rotate emitter offset by item rotation
                rex, rey = rotate_point(ex, ey, item['rot'])
                
                # Translate by final item position
                lx = final_pos[0] + rex
                ly = final_pos[1] + rey
                lz = final_pos[2] + ez
                
                final_lights.append({
                    "position": [lx, ly, lz],
                    "color": emitter['color'],
                    "intensity": emitter['intensity']
                })

        # Write to Lua string
        line = f"        {{ asset_id = '{item['asset_id']}', pos = {{{final_pos[0]}, {final_pos[1]}, {final_pos[2]}}}, rot = {item['rot']}"
        if 'id' in item:
            line = f"        {{ id = '{item['id']}', asset_id = '{item['asset_id']}', pos = {{{final_pos[0]}, {final_pos[1]}, {final_pos[2]}}}, rot = {item['rot']}"
        line += " },\n"
        resolved_layout_str += line

    resolved_layout_str += "    }"
    
    # 4. Reconstruct File Content
    # Replace layout block
    match_start = re.search(r'layout\s*=\s*\{', content)
    if match_start:
        new_content = content[:match_start.start()] + resolved_layout_str
        # Find end of original layout block to append the rest?
        # Actually, simpler to just assume metadata is before layout, and layout is last?
        # The file ends with '}' usually.
        new_content += "\n}" 
    else:
        new_content = content

    # Inject Lights Table (overwrite or insert)
    # Format lights list
    lights_str = "    lights = {\n"
    for l in final_lights:
        p = l['position']
        c = l['color']
        lights_str += f"        {{ position = {{{p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}}}, color = {{{c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}}}, intensity = {l['intensity']} }},\n"
    lights_str += "    },\n"
    
    # Check if 'lights = {' exists
    lights_match = re.search(r'lights\s*=\s*\{', new_content)
    if lights_match:
        # Replace existing lights block
        # Find matching closing brace... this is hard with regex.
        # Let's just find the start, and replace until the next key or end?
        # A bit risky. 
        # Better: Since we parsed manual lights, we can just completely regenerate the file structure if we trust our parsing.
        # But we didn't parse metadata.
        # Hack: Split before 'lights =', take the first part, append new lights, append 'layout =' part.
        
        # If 'layout' comes after 'lights' (standard):
        pre_lights = new_content[:lights_match.start()]
        # find where layout starts
        layout_start = re.search(r'layout\s*=\s*\{', new_content)
        if layout_start:
             new_content = pre_lights + lights_str + new_content[layout_start.start():]
    else:
        # Insert before layout
        layout_start = re.search(r'layout\s*=\s*\{', new_content)
        if layout_start:
             new_content = new_content[:layout_start.start()] + lights_str + new_content[layout_start.start():]
    
    # Write to Game Directory
    os.makedirs(GAME_TILES_DIR, exist_ok=True)
    out_path = os.path.join(GAME_TILES_DIR, filename)
    with open(out_path, 'w') as f:
        f.write(new_content)
    print(f"Compiled {filename} -> {out_path} (Lights: {len(final_lights)})")


if __name__ == "__main__":
    for f in os.listdir(TILES_DIR):
        if f.endswith(".lua"):
            compile_tile(f)
