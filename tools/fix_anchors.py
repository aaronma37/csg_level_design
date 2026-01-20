import json
import os

def fix_anchors(name):
    path = f"csg/{name}.json"
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        data = json.load(f)
    
    data['snap_points'] = {
        "front": { "pos": [0, -2, 0], "rot": 0 },
        "back": { "pos": [0, 2, 0], "rot": 0 },
        "center": { "pos": [0, 0, 0], "rot": 0 }
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Fixed anchors for {name}")

v2_assets = ["timber_wall_v2", "wall_window_v2", "wall_pillar_v2", "door_slot_v2"]
for a in v2_assets:
    fix_anchors(a)
