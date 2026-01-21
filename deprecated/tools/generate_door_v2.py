import json

slot = {
    "name": "door_slot_v2",
    "asset_tags": ["structure", "wall", "door", "v2"],
    "instructions": [
        {"op": "add", "pos": [-24, 0, 40], "size": [16, 4, 80], "color": 2}, # Side left
        {"op": "add", "pos": [24, 0, 40], "size": [16, 4, 80], "color": 2},  # Side right
        {"op": "add", "pos": [0, 0, 70], "size": [32, 4, 20], "color": 2},   # Top beam
    ],
    "snap_points": {
        "door_mount": { "pos": [0, 0, 0], "rot": 0 },
        "tile_snap": { "pos": [0, 16, 0], "rot": 0 }
    }
}
with open("csg/door_slot_v2.json", "w") as f:
    json.dump(slot, f, indent=2)
