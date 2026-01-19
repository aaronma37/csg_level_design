import json

file_path = 'csg/stone_fireplace.json'

with open(file_path, 'r') as f:
    data = json.load(f)

fire_min_x, fire_max_x = -5, 5
fire_min_z, fire_max_z = 4, 12
fire_front_y = -6 # The fire starts at -6. Anything with Y < -6 is "in front".

blocking_blocks = []

for instr in data.get('instructions', []):
    if instr.get('op') == 'add':
        color = instr.get('color')
        if color in [240, 241]: continue # Skip fire itself
        
        pos = instr.get('pos', [0,0,0])
        size = instr.get('size', [0,0,0])
        
        x_min, x_max = pos[0], pos[0] + size[0]
        y_min, y_max = pos[1], pos[1] + size[1]
        z_min, z_max = pos[2], pos[2] + size[2]
        
        # Check overlap in X and Z
        overlap_x = not (x_max <= fire_min_x or x_min >= fire_max_x)
        overlap_z = not (z_max <= fire_min_z or z_min >= fire_max_z)
        
        if overlap_x and overlap_z:
            # Check if it is IN FRONT of the fire (Y < Fire Y)
            # Fire is at Y = -6 to -2.
            # If a block is at Y = -12 to -6, it blocks the view from the front.
            if y_max > -12 and y_min < -6:
                blocking_blocks.append({'pos': pos, 'size': size, 'color': color, 'y_range': f"{y_min}..{y_max}"})

print(f"Blocking Blocks found: {len(blocking_blocks)}")
for b in blocking_blocks[:5]: # Show first 5
    print(b)
