import json
import sys

def check_bounds(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    for instr in data.get('instructions', []):
        if 'pos' in instr and 'size' in instr:
            pos = instr['pos']
            size = instr['size']
            min_x = min(min_x, pos[0]); max_x = max(max_x, pos[0] + size[0])
            min_y = min(min_y, pos[1]); max_y = max(max_y, pos[1] + size[1])
            min_z = min(min_z, pos[2]); max_z = max(max_z, pos[2] + size[2])
            
    print(f"File: {file_path}")
    print(f"  X: {min_x} to {max_x} (Center: {(min_x + max_x)/2})")
    print(f"  Y: {min_y} to {max_y} (Center: {(min_y + max_y)/2})")
    print(f"  Z: {min_z} to {max_z}")

for path in sys.argv[1:]:
    check_bounds(path)
