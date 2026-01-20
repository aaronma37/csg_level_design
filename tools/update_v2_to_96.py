import json
import os

def update_asset(name, height):
    path = f"csg/{name}.json"
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        data = json.load(f)
    
    for inst in data['instructions']:
        if 'size' in inst:
            # If it's a vertical component (size[2] > size[0/1]), stretch it
            if inst['size'][2] >= 70:
                inst['size'][2] = height
                inst['pos'][2] = height // 2
            # Handle the top trim/beam
            elif inst['pos'][2] > 60:
                inst['pos'][2] = height - (inst['size'][2] // 2)
                
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated {name} to {height}v")

v2_assets = ["timber_wall_v2", "wall_window_v2", "wall_pillar_v2", "door_slot_v2"]
for a in v2_assets:
    update_asset(a, 96)
