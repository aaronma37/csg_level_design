import json

# Target: 32 wide, 80 tall, 4 thick
wall = {
    "name": "timber_wall_v2",
    "asset_tags": ["structure", "wall", "wood", "v2"],
    "instructions": [
        # Main Wall Body (Centered at 0,0, Z-up height 0-80)
        {
            "op": "add",
            "pos": [0, 0, 40],
            "size": [32, 4, 80],
            "color": 2 # Stone/Wood base color
        },
        # Top Trim (Visual marker for height)
        {
            "op": "add",
            "pos": [0, 0, 78],
            "size": [34, 6, 4],
            "color": 45 # Gold/Trim color
        }
    ],
    "snap_points": {
        "back": {
            "pos": [0, 2, 0], # Back of the 4-thick wall
            "rot": 0
        },
        "front": {
            "pos": [0, -2, 0], # Front of the 4-thick wall
            "rot": 0
        },
        "tile_snap": {
            "pos": [0, 16, 0], # EXACT edge of a 32x32 tile
            "rot": 0
        }
    }
}

with open("csg/timber_wall_v2.json", "w") as f:
    json.dump(wall, f, indent=2)
print("Created csg/timber_wall_v2.json with 80v height and tile_snap anchor at Y=16.")
