import json

base_file = 'csg/timber_wall_straight_32.json'
out_file = 'csg/timber_wall_post_32.json'

with open(base_file, 'r') as f:
    data = json.load(f)

# 1. Beefy Vertical Post
# X: Centered at 16. Size 12. Pos 10.
# Y: 0..12 (Match wall beams).
# Z: 0..96.
post_instr = {
    "op": "add",
    "pos": [10, 0, 0],
    "size": [12, 12, 96],
    "color": 2
}
data['instructions'].append(post_instr)

# 2. Beefy Angle Brace (45 degrees)
brace_start_z = 72
brace_end_z = 96
brace_start_y = 0
step = 2

for i in range(0, brace_end_z - brace_start_z, step):
    z = brace_start_z + i
    y = brace_start_y - i
    
    brace_block = {
        "op": "add",
        "pos": [11, y - step, z],
        "size": [10, step + 1, step + 1],
        "color": 2
    }
    data['instructions'].append(brace_block)

# 3. Ceiling Crossbeam
# Extends from back of wall past the brace.
# Wall Back: 12. Brace tip is at -24.
# Extension to -32.
# X: 10..22. Z: 90..96 (to align with wall top beam).
ceiling_beam = {
    "op": "add",
    "pos": [10, -32, 90],
    "size": [12, 44, 6], # 12 - (-32) = 44 length
    "color": 2
}
data['instructions'].append(ceiling_beam)

data['name'] = 'timber_wall_post_32'

with open(out_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Created beefy {out_file} with brace and crossbeam")
