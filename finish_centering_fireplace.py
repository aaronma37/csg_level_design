import json

file_path = 'csg/stone_fireplace.json'

with open(file_path, 'r') as f:
    data = json.load(f)

count = 0
for instr in data.get('instructions', []):
    # 'add' was already shifted. Shift everything else.
    if instr.get('op') != 'add':
        if 'pos' in instr:
            pos = instr['pos']
            # Apply the same shift: X - 25, Y - 12
            pos[0] -= 25
            pos[1] -= 12
            instr['pos'] = pos
            count += 1
        elif 'points' in instr:
            # If there are point clouds (unlikely for subtract but possible)
            pass 

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Applied shift to {count} non-add instructions in {file_path}")
