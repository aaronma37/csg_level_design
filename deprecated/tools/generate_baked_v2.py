import json

def create_baked_tile(name, wall_instructions, tags):
    # Standard Floor Base (32x32x1, centered at 0,0)
    instructions = [
        {"op": "add", "pos": [0, 0, 0], "size": [32, 32, 1], "color": 2}
    ]
    # Add the wall/feature instructions
    instructions.extend(wall_instructions)
    
    data = {
        "name": name,
        "asset_tags": tags + ["v2", "baked"],
        "instructions": instructions,
        "snap_points": { "center": {"pos": [0,0,0], "rot": 0} }
    }
    with open(f"csg/{name}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Created Baked Tile: {name}")

# Wall is 4 thick. 
# To be flush with edge (16), center must be at 14 (14+2=16).
WALL_Y = 14

# 1. Straight Wall Baked
create_baked_tile("wall_straight_baked_v2", [
    {"op": "add", "pos": [0, WALL_Y, 48], "size": [32, 4, 96], "color": 2}
], ["structure", "wall", "straight"])

# 2. Window Wall Baked
create_baked_tile("wall_window_baked_v2", [
    {"op": "add", "pos": [0, WALL_Y, 48], "size": [32, 4, 96], "color": 2},
    {"op": "sub", "pos": [0, WALL_Y, 45], "size": [16, 10, 24]}
], ["structure", "wall", "window"])

# 3. Door Slot Baked
create_baked_tile("wall_door_baked_v2", [
    {"op": "add", "pos": [-12, WALL_Y, 48], "size": [8, 4, 96], "color": 2}, # Side L
    {"op": "add", "pos": [12, WALL_Y, 48], "size": [8, 4, 96], "color": 2},  # Side R
    {"op": "add", "pos": [0, WALL_Y, 80], "size": [32, 4, 32], "color": 2},  # Top
], ["structure", "wall", "doorway"])

# 4. Corner Wall Baked (NW Corner)
# North wall at Y=14, West wall at X=-14
create_baked_tile("wall_corner_nw_baked_v2", [
    {"op": "add", "pos": [0, 14, 48], "size": [32, 4, 96], "color": 2}, # North
    {"op": "add", "pos": [-14, 0, 48], "size": [4, 32, 96], "color": 2} # West
], ["structure", "wall", "corner"])

