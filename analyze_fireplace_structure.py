import json

file_path = 'csg/stone_fireplace.json'

with open(file_path, 'r') as f:
    data = json.load(f)

fire_voxels = []
stone_voxels = []

for instr in data.get('instructions', []):
    if instr.get('op') == 'add':
        color = instr.get('color')
        pos = instr.get('pos', [0,0,0])
        size = instr.get('size', [0,0,0])
        
        # Calculate center of this block
        center = [pos[0] + size[0]/2, pos[1] + size[1]/2, pos[2] + size[2]/2]
        
        if color in [240, 241]: # Fire
            fire_voxels.append({'pos': pos, 'size': size, 'center': center})
        elif color == 22: # Stone (Dark)
            stone_voxels.append({'pos': pos, 'size': size, 'center': center})

print(f"Total Fire Blocks: {len(fire_voxels)}")
if fire_voxels:
    min_f = [min(v['pos'][i] for v in fire_voxels) for i in range(3)]
    max_f = [max(v['pos'][i] + v['size'][i] for v in fire_voxels) for i in range(3)]
    center_f = [(min_f[i] + max_f[i])/2 for i in range(3)]
    print(f"Fire Bounds: X:{min_f[0]}..{max_f[0]}, Y:{min_f[1]}..{max_f[1]}, Z:{min_f[2]}..{max_f[2]}")
    print(f"Fire Center: {center_f}")

print(f"Total Stone Blocks: {len(stone_voxels)}")
if stone_voxels:
    min_s = [min(v['pos'][i] for v in stone_voxels) for i in range(3)]
    max_s = [max(v['pos'][i] + v['size'][i] for v in stone_voxels) for i in range(3)]
    center_s = [(min_s[i] + max_s[i])/2 for i in range(3)]
    print(f"Stone Bounds: X:{min_s[0]}..{max_s[0]}, Y:{min_s[1]}..{max_s[1]}, Z:{min_s[2]}..{max_s[2]}")
    print(f"Stone Center: {center_s}")
