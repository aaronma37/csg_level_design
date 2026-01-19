import json
import sys

file_path = sys.argv[1] if len(sys.argv) > 1 else 'csg/stone_fireplace.json'

def check_bounds(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    for instr in data.get('instructions', []):
        if instr.get('op') == 'add':
            pos = instr.get('pos', [0, 0, 0])
            size = instr.get('size', [0, 0, 0])
            
            min_x = min(min_x, pos[0])
            min_y = min(min_y, pos[1])
            min_z = min(min_z, pos[2])
            
            max_x = max(max_x, pos[0] + size[0])
            max_y = max(max_y, pos[1] + size[1])
            max_z = max(max_z, pos[2] + size[2])
            
    print(f"Bounds for {file_path}:")
    print(f"X: {min_x} to {max_x} (Width: {max_x - min_x}, Center: {(min_x + max_x) / 2})")
    print(f"Y: {min_y} to {max_y} (Height: {max_y - min_y}, Center: {(min_y + max_y) / 2})")
    print(f"Z: {min_z} to {max_z} (Depth: {max_z - min_z}, Center: {(min_z + max_z) / 2})")

check_bounds(file_path)
