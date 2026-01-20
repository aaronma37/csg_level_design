import json

def save_v2(name, instructions, tags):
    wall = {
        "name": name,
        "asset_tags": tags + ["v2"],
        "instructions": instructions,
        "snap_points": { "tile_snap": { "pos": [0, 16, 0], "rot": 0 } }
    }
    with open(f"csg/{name}.json", "w") as f:
        json.dump(wall, f, indent=2)

# 1. Window Wall V2
save_v2("wall_window_v2", [
    {"op": "add", "pos": [0, 0, 40], "size": [32, 4, 80], "color": 2},
    {"op": "sub", "pos": [0, 0, 45], "size": [16, 10, 24]} # Window hole
], ["structure", "wall", "window"])

# 2. Pillar Wall V2
save_v2("wall_pillar_v2", [
    {"op": "add", "pos": [0, 0, 40], "size": [32, 4, 80], "color": 2},
    {"op": "add", "pos": [-14, -2, 40], "size": [4, 6, 80], "color": 2}, # Pillar left
    {"op": "add", "pos": [14, -2, 40], "size": [4, 6, 80], "color": 2}   # Pillar right
], ["structure", "wall", "pillar"])

