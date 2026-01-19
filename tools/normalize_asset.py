import json
import sys
import os

def normalize_asset(file_path, is_wall=False):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    instructions = data.get('instructions', [])
    if not instructions:
        print(f"No instructions found in {file_path}")
        return

    min_coords = [float('inf')] * 3
    max_coords = [float('-inf')] * 3
    has_geometry = False

    for instr in instructions:
        if 'pos' in instr and 'size' in instr:
            has_geometry = True
            pos = instr['pos']
            size = instr['size']
            for i in range(3):
                min_coords[i] = min(min_coords[i], pos[i])
                max_coords[i] = max(max_coords[i], pos[i] + size[i])
        elif 'points' in instr:
            has_geometry = True
            base_pos = instr.get('pos', [0, 0, 0])
            for pt in instr['points']:
                for i in range(3):
                    val = base_pos[i] + pt[i]
                    min_coords[i] = min(min_coords[i], val)
                    max_coords[i] = max(max_coords[i], val + 1)

    if not has_geometry:
        return

    # COA 1: Anchor-Based Normalization
    # X is always centered. Z is always grounded.
    # Y is anchored to the North Edge (6) if it's a wall, else centered.
    
    center_x = (min_coords[0] + max_coords[0]) / 2
    center_y = (min_coords[1] + max_coords[1]) / 2
    
    offset = [
        -int(round(center_x)),
        0, # Calculated below
        -int(round(min_coords[2]))
    ]
    
    if is_wall:
        # Lock the North Edge (Max Y) to local 6.
        # This keeps the 'Wall Core' at [-6, 6] even with southern protrusions.
        offset[1] = 6 - int(round(max_coords[1]))
    else:
        offset[1] = -int(round(center_y))

    if offset == [0, 0, 0]:
        print(f"Asset {file_path} already normalized.")
        return

    print(f"Normalizing {file_path} (Wall Mode: {is_wall})... Shift: {offset}")

    for instr in instructions:
        if 'pos' in instr:
            pos = instr['pos']
            for i in range(3):
                pos[i] += offset[i]
            instr['pos'] = pos
        elif 'points' in instr and 'pos' not in instr:
            for pt in instr['points']:
                for i in range(3):
                    pt[i] += offset[i]

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    args = sys.argv[1:]
    is_wall = False
    if "--wall" in args:
        is_wall = True
        args.remove("--wall")
    
    for path in args:
        normalize_asset(path, is_wall=is_wall)
