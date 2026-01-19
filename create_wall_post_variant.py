import json

base_file = 'csg/timber_wall_straight_32.json'
out_file = 'csg/timber_wall_post_32.json'

with open(base_file, 'r') as f:
    data = json.load(f)

# Add Vertical Post
# X: Centered at 16. Size 6. Pos 13.
# Y: Sticking out? Wall is at Y=8..12. Let's place post at Y=6..12 (Size 6).
# Z: 0..96.
post_instr = {
    "op": "add",
    "pos": [13, 6, 0],
    "size": [6, 6, 96],
    "color": 2 # Dark Wood
}

data['instructions'].append(post_instr)
data['name'] = 'timber_wall_post_32'

with open(out_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Created {out_file}")
