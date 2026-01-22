import json
import os
import random
import argparse
import collections
import math
from themes import THEMES

# --- CONFIGURATION ---
TILE_REGISTRY_PATH = "csg_assets/tile_registry.json"
ASSET_REGISTRY_PATH = "csg/asset_registry.json"
CSG_DIR = "csg"
OUTPUT_DIR = "csg_assets/scenes"

# --- UTILS ---

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r') as f: return json.load(f)

def query_registry(registry, query_def):
    """
    Query a registry (dict) for keys matching tags.
    query_def: {"include": [...], "exclude": [...]} 
    """
    if not query_def: return []
    include = query_def.get("include", [])
    exclude = query_def.get("exclude", [])
    
    results = []
    for tid, data in registry.items():
        tags = data.get('tile_tags', data.get('asset_tags', []))
        if include and not all(t in tags for t in include): continue
        if exclude and any(t in tags for t in exclude): continue
        results.append(tid)
    return results

def get_random_by_role(registry, theme, role_name):
    """
    Helper to get a single random ID for a named role in the theme.
    """
    query_def = theme.get(role_name)
    if not query_def: return None
    candidates = query_registry(registry, query_def)
    if not candidates: return None
    return random.choice(candidates)

def rotate_point(x, y, angle_deg):
    if angle_deg == 0: return x, y
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a

def load_layout_recursively(asset_id, parent_pos=(0,0,0), parent_rot=0):
    path = os.path.join(CSG_DIR, f"{asset_id}.json")
    if not os.path.exists(path): return []
    with open(path, 'r') as f: data = json.load(f)
    items = data if isinstance(data, list) else data.get('layout', [])
    if not items and not isinstance(data, list):
        # Base case: It's a leaf asset, return itself placed in world
        return [{'asset_id': asset_id, 'pos': list(parent_pos), 'rot': parent_rot}]
    
    flat_items = []
    for item in items:
        aid = item['asset_id']
        lx, ly, lz = item.get('pos', [0,0,0])
        lr = item.get('rot', 0)
        
        # Transform local to parent space
        rx, ry = rotate_point(lx, ly, parent_rot) 
        gx = parent_pos[0] + rx
        gy = parent_pos[1] + ry
        gz = parent_pos[2] + lz
        
        gr = (lr + parent_rot) % 360
        
        child_path = os.path.join(CSG_DIR, f"{aid}.json")
        is_coll = False
        if os.path.exists(child_path):
             with open(child_path, 'r') as cf:
                cdata = json.load(cf)
                if isinstance(cdata, list) or (isinstance(cdata, dict) and 'layout' in cdata):
                    is_coll = True
        
        if is_coll:
            flat_items.extend(load_layout_recursively(aid, (gx, gy, gz), gr))
        else:
            flat_items.append({'asset_id': aid, 'pos': [gx, gy, gz], 'rot': gr})
            
    return flat_items

def get_path(start, end, width, height, blocked_cells):
    queue = collections.deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        x, z = path[-1]
        if (x, z) == end: return path
        for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, nz = x + dx, z + dz
            if 0 <= nx < width and 0 <= nz < height and (nx, nz) not in seen and (nx, nz) not in blocked_cells:
                queue.append(path + [(nx, nz)])
                seen.add((nx, nz))
    return None

def generate_room(name, width, height, exits, theme_name="tavern"):
    if theme_name not in THEMES:
        print(f"Error: Theme '{theme_name}' not found. Available: {list(THEMES.keys())}")
        return

    theme = THEMES[theme_name]
    tile_reg = load_json(TILE_REGISTRY_PATH)
    asset_reg = load_json(ASSET_REGISTRY_PATH)
    
    grid = [[{"tile_id": None, "rot": 0, "reserved": False} for _ in range(width)] for _ in range(height)]
    blocked_cells = set()
    extra_assets = [] 

    # --- PHASE 1: SKELETON (Theme Driven) ---
    
    corner_nw_id = get_random_by_role(tile_reg, theme, "corner_nw")
    door_north_id = get_random_by_role(tile_reg, theme, "door_north")
    door_west_id = get_random_by_role(tile_reg, theme, "door_west")
    wall_north_id = get_random_by_role(tile_reg, theme, "wall_north")
    wall_north_mega_id = get_random_by_role(tile_reg, theme, "wall_north_mega")
    wall_west_id = get_random_by_role(tile_reg, theme, "wall_west")
    wall_west_mega_id = get_random_by_role(tile_reg, theme, "wall_west_mega")
    floor_ent_id = get_random_by_role(tile_reg, theme, "floor_entrance")
    
    if corner_nw_id:
        grid[0][0] = {"tile_id": corner_nw_id, "rot": 0, "reserved": True}
        blocked_cells.add((0, 0))

    entrance_pos = (width // 2, height - 1)
    if floor_ent_id:
        grid[entrance_pos[1]][entrance_pos[0]] = {"tile_id": floor_ent_id, "rot": 0, "reserved": True}
    
    exit_positions = []
    
    if exits.get('north') and door_north_id:
        grid[0][width // 2] = {"tile_id": door_north_id, "rot": 0, "reserved": True}
        exit_positions.append((width // 2, 0))
    
    if exits.get('west') and door_west_id:
        grid[height // 2][0] = {"tile_id": door_west_id, "rot": 90, "reserved": True}
        exit_positions.append((0, height // 2))

    # Backdrop Walls - North (z=0)
    x = 1
    while x < width:
        if grid[0][x]["tile_id"] is not None:
            x += 1; continue

        placed_mega = False
        if wall_north_mega_id and x + 3 < width:
            is_clear = True
            for i in range(4):
                if grid[0][x+i]["tile_id"] is not None: is_clear = False; break
            
            if is_clear and random.random() < 0.6:
                anchor_x = x + 1
                grid[0][anchor_x] = {"tile_id": wall_north_mega_id, "rot": 0, "reserved": True}
                for i in range(4):
                    if (x+i) != anchor_x: grid[0][x+i] = {"tile_id": "linked", "rot": 0, "reserved": True}
                    blocked_cells.add((x+i, 0))
                x += 4; placed_mega = True
        
        if not placed_mega:
            w_id = get_random_by_role(tile_reg, theme, "wall_north") or wall_north_id
            if w_id:
                grid[0][x] = {"tile_id": w_id, "rot": 0, "reserved": True}
                blocked_cells.add((x, 0))
            x += 1

    # Backdrop Walls - West (x=0)
    z = 1
    while z < height:
        if grid[z][0]["tile_id"] is not None:
            z += 1; continue

        placed_mega = False
        if wall_west_mega_id and z + 3 < height:
            is_clear = True
            for i in range(4):
                if grid[z+i][0]["tile_id"] is not None: is_clear = False; break
            
            if is_clear and random.random() < 0.6:
                anchor_z = z + 1
                grid[anchor_z][0] = {"tile_id": wall_west_mega_id, "rot": 90, "reserved": True}
                for i in range(4):
                    if (z+i) != anchor_z: grid[z+i][0] = {"tile_id": "linked", "rot": 90, "reserved": True}
                    blocked_cells.add((0, z+i))
                z += 4; placed_mega = True

        if not placed_mega:
            w_id = get_random_by_role(tile_reg, theme, "wall_west") or wall_west_id
            if w_id:
                grid[z][0] = {"tile_id": w_id, "rot": 90, "reserved": True}
                blocked_cells.add((0, z))
            z += 1

    # --- PHASE 2: WALKABILITY ---
    for exit_pos in exit_positions:
        path = get_path(entrance_pos, exit_pos, width, height, blocked_cells)
        if path:
            for cell in path: grid[cell[1]][cell[0]]["reserved"] = True

    # --- PHASE 3: FILLING ---
    
    # 1. Features (North Wall)
    valid_feature_slots = [x for x in range(1, width-1) if not grid[1][x]["reserved"] and not grid[1][x]["tile_id"]]
    if valid_feature_slots and "features_north" in theme:
        feature_defs = theme["features_north"]
        random.shuffle(valid_feature_slots) 
        
        for f_def in feature_defs:
            if random.random() > 0.5: continue 
            f_id = None; f_type = f_def.get("type", "tile")
            candidates = query_registry(tile_reg if f_type == "tile" else asset_reg, f_def)
            if candidates: f_id = random.choice(candidates)
                
            if f_id:
                for slot_x in valid_feature_slots:
                    block_w, block_h = 1, 1
                    if f_type == "tile": block_w, block_h = tile_reg[f_id].get("block_size", [1, 1])
                    fits = True; cells_to_reserve = []
                    
                    for bx in range(block_w):
                        for by in range(block_h):
                            check_x = slot_x + bx; check_y = 1 + by
                            if check_x >= width or check_y >= height or grid[check_y][check_x]["reserved"] or grid[check_y][check_x]["tile_id"]:
                                fits = False; break
                            
                            # Check Backdrop for Mega Wall Posts (Edge tiles)
                            backdrop = grid[0][check_x]
                            if backdrop["tile_id"] and ("mega" in backdrop["tile_id"] or backdrop["tile_id"] == "linked"):
                                # Check if this is an edge of the mega block
                                # Left neighbor
                                is_edge = False
                                if check_x > 0:
                                    left = grid[0][check_x-1]
                                    if left["tile_id"] != backdrop["tile_id"] and left["tile_id"] != "linked" and backdrop["tile_id"] != "linked":
                                         # If current is anchor, left must be linked to be same group.
                                         # If current is linked, left must be anchor or linked to same group.
                                         # Simplified: Just assume if IDs change, it's a boundary.
                                         is_edge = True
                                    elif left["tile_id"] == "linked" and backdrop["tile_id"] == "linked":
                                         # Both linked, but are they same group? 
                                         # procedural gen marks blocks sequentially. 
                                         # If we have [Mega A, Linked, Linked, Linked] [Mega B, Linked...]
                                         # The boundary between Linked and Mega B is clear.
                                         # The boundary between Linked and Linked is invisible.
                                         pass
                                elif check_x == 0: is_edge = True
                                
                                # Right neighbor
                                if check_x < width - 1:
                                    right = grid[0][check_x+1]
                                    # If current is linked, right might be anchor?
                                    # This heuristic is tricky with "linked".
                                    # Better: When we place the mega wall, we mark the *edges*?
                                    # Or just look at the asset definitions? 
                                    # "wall_north_mega" is 4 tiles. 
                                    # If we just skip check_x if it aligns with the start/end of the mega placement?
                                    pass
                                
                                # Robust Check:
                                # We don't store "Group ID".
                                # But we know North Wall generation is strictly sequential L->R.
                                # So [Anchor, Linked, Linked, Linked] is the pattern.
                                # Edge tiles are Anchor (Left) and Anchor+3 (Right).
                                # If current tile is Anchor -> Left Edge.
                                # If current tile is "linked" and right neighbor is NOT "linked" (and not part of this group)?
                                
                                # Let's try to detect if we are at Anchor or Anchor+3.
                                # If backdrop["tile_id"] != "linked": It is the Anchor (Left Edge). -> SKIP
                                if backdrop["tile_id"] != "linked":
                                    fits = False; break
                                
                                # If it IS linked, we need to know if it's the last one.
                                # Look ahead.
                                if check_x + 1 < width:
                                    right = grid[0][check_x+1]
                                    if right["tile_id"] != "linked":
                                        # Next is not linked, so we are the last link (Right Edge). -> SKIP
                                        fits = False; break
                                else:
                                    # End of map -> Right Edge. -> SKIP
                                    fits = False; break

                            cells_to_reserve.append((check_x, check_y))
                        if not fits: break
                    
                    if fits:
                        if f_type == "tile":
                            grid[1][slot_x] = {"tile_id": f_id, "rot": 180, "reserved": True} 
                            for (rx, ry) in cells_to_reserve:
                                if rx == slot_x and ry == 1: continue
                                grid[ry][rx]["reserved"] = True
                                grid[ry][rx]["tile_id"] = "linked" 
                        else:
                            extra_assets.append({"asset_id": f_id, "pos": [slot_x * 32, 16, 0], "rot": 180})
                            for (rx, ry) in cells_to_reserve: grid[ry][rx]["reserved"] = True
                        valid_feature_slots = [s for s in valid_feature_slots if s not in [c[0] for c in cells_to_reserve]]
                        break 
                        
    # 2. Features (Central - Furniture)
    if "features_central" in theme:
        feature_defs = theme["features_central"]
        # Grid scan (safe zone away from walls)
        safe_zone_z = list(range(3, height-2))
        safe_zone_x = list(range(2, width-2))
        random.shuffle(safe_zone_z); random.shuffle(safe_zone_x)

        for f_def in feature_defs:
            if random.random() > f_def.get("chance", 0.5): continue
            
            f_id = None; f_type = f_def.get("type", "tile")
            candidates = query_registry(tile_reg if f_type == "tile" else asset_reg, f_def)
            if candidates: f_id = random.choice(candidates)
            
            if f_id:
                # Try to place multiple instances (up to density limit)
                placed_count = 0
                target_count = f_def.get("count", 3) # Default 3 tables
                
                # Iterate through all safe slots
                for z in safe_zone_z:
                    if placed_count >= target_count: break
                    for x in safe_zone_x:
                        if placed_count >= target_count: break
                        
                        block_w, block_h = 1, 1
                        if f_type == "tile": block_w, block_h = tile_reg[f_id].get("block_size", [1, 1])
                        
                        fits = True; cells_to_reserve = []
                        for bx in range(block_w):
                            for by in range(block_h):
                                check_x = x + bx; check_y = z + by
                                if check_x >= width or check_y >= height or grid[check_y][check_x]["reserved"] or grid[check_y][check_x]["tile_id"]:
                                    fits = False; break
                                cells_to_reserve.append((check_x, check_y))
                            if not fits: break
                        
                        if fits:
                            if f_type == "tile":
                                grid[z][x] = {"tile_id": f_id, "rot": 0, "reserved": True}
                                for (rx, ry) in cells_to_reserve:
                                    if rx == x and ry == z: continue
                                    grid[ry][rx]["reserved"] = True; grid[ry][rx]["tile_id"] = "linked"
                            else:
                                extra_assets.append({"asset_id": f_id, "pos": [x * 32, z * 32, 0], "rot": 0})
                                for (rx, ry) in cells_to_reserve: grid[ry][rx]["reserved"] = True
                            placed_count += 1
                            # Do not break here, try to place more? 
                            # If we don't break, we might place tables adjacent to each other tightly.
                            # Let's keep scanning.
                            pass


    # 3. Floor Filling
    for z in range(height):
        for x in range(width):
            if grid[z][x]["tile_id"] is None:
                f_id = get_random_by_role(tile_reg, theme, "floor_primary")
                grid[z][x]["tile_id"] = f_id
                
                clutter_def = theme.get("clutter")
                if clutter_def and not grid[z][x]["reserved"] and random.random() < clutter_def.get("chance", 0.0):
                     pass

    # --- EXPORT ---
    final_layout = []
    for item in extra_assets: 
        final_layout.extend(load_layout_recursively(item['asset_id'], item['pos'], item['rot']))
        
    lua_output = os.path.join(OUTPUT_DIR, f"{name}.lua")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(lua_output, 'w') as f:
        f.write(f"-- Theme: {theme_name}, Scene: {name}\nreturn {{\n    tiles = {{-- \n")
        for z in range(height):
            for x in range(width):
                t = grid[z][x]
                tid = t['tile_id']
                if tid == "linked": continue 
                
                tid = tid or 'empty' 
                f.write(f"        {{ tile_id = '{tid}', pos = {{{x}, {z}}}, height = 0, rot = {t['rot']} }},\n")
        f.write("    },\n    layout = {\n")
        for item in final_layout:
            f.write(f"        {{ asset_id = '{item['asset_id']}', pos = {{{int(item['pos'][0])}, {int(item['pos'][1])}, {int(item['pos'][2])}}}, rot = {int(item['rot'])} }},\n")
        f.write("    }\n}\n")
    print(f"Generated {lua_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="generated_scene")
    parser.add_argument("--width", type=int, default=12)
    parser.add_argument("--height", type=int, default=12)
    parser.add_argument("--north", action="store_true", help="Add North exit")
    parser.add_argument("--west", action="store_true", help="Add West exit")
    parser.add_argument("--theme", default="tavern", help="Theme to use (tavern, nature)")
    args = parser.parse_args()
    
    generate_room(args.name, args.width, args.height, {"north": args.north, "west": args.west}, args.theme)