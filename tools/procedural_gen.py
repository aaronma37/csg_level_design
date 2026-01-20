import json
import os
import random
import argparse
import collections
import math

TILE_REGISTRY_PATH = "csg_assets/tile_registry.json"
ASSET_REGISTRY_PATH = "csg/asset_registry.json"
CSG_DIR = "csg"
OUTPUT_DIR = "csg_assets/scenes"

def load_json(path):
    with open(path, 'r') as f: return json.load(f)

def query_registry(registry, include=None, exclude=None, key='tile_tags'):
    results = []
    for tid, data in registry.items():
        tags = data.get(key, [])
        if include and not all(t in tags for t in include): continue
        if exclude and any(t in tags for t in exclude): continue
        results.append(tid)
    return results

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
        return [{'asset_id': asset_id, 'pos': list(parent_pos), 'rot': parent_rot}]
    flat_items = []
    for item in items:
        aid = item['asset_id']
        lx, ly, lz = item.get('pos', [0,0,0])
        lr = item.get('rot', 0)
        rx, ry = rotate_point(lx, ly, parent_rot)
        gx, gy, gz = parent_pos[0] + rx, parent_pos[1] + ry, parent_pos[2] + lz
        gr = (lr + parent_rot) % 360
        child_path = os.path.join(CSG_DIR, f"{aid}.json")
        is_coll = os.path.exists(child_path)
        if is_coll:
            with open(child_path, 'r') as cf:
                cdata = json.load(cf)
                if isinstance(cdata, list) or (isinstance(cdata, dict) and 'layout' in cdata):
                    flat_items.extend(load_layout_recursively(aid, (gx, gy, gz), gr))
                    continue
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

def generate_room(name, width, height, exits):
    tile_reg = load_json(TILE_REGISTRY_PATH)
    grid = [[{"tile_id": None, "rot": 0, "reserved": False} for _ in range(width)] for _ in range(height)]
    blocked_cells = set()
    initial_assets = []

    # --- PHASE 1: SKELETON ---
    # NW Corner
    grid[0][0] = {"tile_id": "wall_corner_nw_32", "rot": 0, "reserved": True}
    blocked_cells.add((0, 0))

    # Exits
    entrance_pos = (width // 2, height - 1)
    grid[entrance_pos[1]][entrance_pos[0]] = {"tile_id": "floor_bevel_32", "rot": 0, "reserved": True}
    exit_positions = []
    if exits.get('north'):
        grid[0][width // 2] = {"tile_id": "wall_door_north_32", "rot": 0, "reserved": True}
        exit_positions.append((width // 2, 0))
    if exits.get('west'):
        # Rotate a North door 270 degrees to make it a West door
        grid[height // 2][0] = {"tile_id": "wall_door_north_32", "rot": 270, "reserved": True}
        exit_positions.append((0, height // 2))

    # Backdrop Walls (Using only V2 North-facing pool)
    v2_pool = query_registry(tile_reg, include=["wall", "north", "v2"], exclude=["doorway", "corner"])
    if not v2_pool: v2_pool = ["wall_straight_v2"]
    
    # North wall (z=0) - rot 0
    for x in range(1, width):
        if grid[0][x]["tile_id"] is None:
            grid[0][x] = {"tile_id": random.choice(v2_pool), "rot": 0, "reserved": True}
            blocked_cells.add((x, 0))
    # West wall (x=0) - rot 270 (Turns North wall to West)
    for z in range(1, height):
        if grid[z][0]["tile_id"] is None:
            grid[z][0] = {"tile_id": random.choice(v2_pool), "rot": 270, "reserved": True}
            blocked_cells.add((0, z))

    # --- PHASE 2: WALKABILITY ---
    for exit_pos in exit_positions:
        path = get_path(entrance_pos, exit_pos, width, height, blocked_cells)
        if path:
            for cell in path: grid[cell[1]][cell[0]]["reserved"] = True

    # --- PHASE 3: FILLING ---
    # Fireplace (Asset)
    north_slots = [x for x in range(1, width-1) if not grid[0][x]["reserved"]]
    if north_slots and random.random() > 0.3:
        slot_x = random.choice(north_slots)
        initial_assets.append({"asset_id": "collection_fireplace_nook", "pos": [slot_x * 32, 16, 0], "rot": 180})
        if 1 < height: grid[1][slot_x]["reserved"] = True

    # Fill Interior
    floor_pool = query_registry(tile_reg, include=["walkable", "floor"])
    for z in range(height):
        for x in range(width):
            if grid[z][x]["tile_id"] is None:
                grid[z][x]["tile_id"] = random.choice(floor_pool)

    # --- EXPORT ---
    final_layout = []
    for item in initial_assets: final_layout.extend(load_layout_recursively(item['asset_id'], item['pos'], item['rot']))
    lua_output = os.path.join(OUTPUT_DIR, f"{name}.lua")
    with open(lua_output, 'w') as f:
        f.write(f"-- Unified Wall scene: {name}\nreturn {{\n    tiles = {{\n")
        for z in range(height):
            for x in range(width):
                t = grid[z][x]
                f.write(f"        {{ tile_id = '{t['tile_id']}', pos = {{{x}, {z}}}, height = 0, rot = {t['rot']} }},\n")
        f.write("    },\n    layout = {\n")
        for item in final_layout:
            f.write(f"        {{ asset_id = '{item['asset_id']}', pos = {{{int(item['pos'][0])}, {int(item['pos'][1])}, {int(item['pos'][2])}}}, rot = {int(item['rot'])} }},\n")
        f.write("    }\n}\n")
    print(f"Unified Room generated: {lua_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="unified_tavern")
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--north", action="store_true")
    parser.add_argument("--west", action="store_true")
    args = parser.parse_args()
    generate_room(args.name, args.width, args.height, {"north": args.north, "west": args.west})
