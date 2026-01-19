import json
import sys
import os

def normalize_asset(file_path):
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

    # 1. Calculate Bounds
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
            # Points are typically relative to a 'pos' if it exists, or absolute?
            # In existing files, 'pos' is often [0,0,0] for point clouds.
            base_pos = instr.get('pos', [0, 0, 0])
            for pt in instr['points']:
                for i in range(3):
                    # Point coord + Base Pos
                    val = base_pos[i] + pt[i]
                    min_coords[i] = min(min_coords[i], val)
                    max_coords[i] = max(max_coords[i], val + 1) # Points are 1x1x1 voxels

    if not has_geometry:
        print(f"No geometry instructions found in {file_path}")
        return

    center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]
    
    # Offset Calculation: Center X/Y at 0. Align Z-min to 0.
    offset = [
        -center[0],      # Shift X to 0
        -center[1],      # Shift Y to 0
        -min_coords[2]   # Shift Z so bottom touches 0
    ]

    # Round to nearest integer
    offset = [int(round(x)) for x in offset]

    if offset == [0, 0, 0]:
        print(f"Asset {file_path} is already normalized.")
        return

    print(f"Normalizing {file_path}...")
    print(f"  Bounds: {min_coords} to {max_coords}")
    print(f"  Shift: {offset}")

    # 2. Apply Shift
    count = 0
    for instr in instructions:
        if 'pos' in instr and 'size' in instr:
            # Box Primitive
            pos = instr['pos']
            for i in range(3):
                pos[i] += offset[i]
            instr['pos'] = pos
            count += 1
        elif 'points' in instr:
            # Point Cloud
            # If we shift the base 'pos', it shifts all points.
            if 'pos' in instr:
                pos = instr['pos']
                for i in range(3):
                    pos[i] += offset[i]
                instr['pos'] = pos
                count += 1
            else:
                # No pos field? Add one or shift points manually?
                # Usually 'pos' exists. If not, shift points.
                for pt in instr['points']:
                    for i in range(3):
                        pt[i] += offset[i]
                count += 1

    # 3. Save
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Updated {count} instructions.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/normalize_asset.py <path_to_asset.json>")
    else:
        for path in sys.argv[1:]:
            normalize_asset(path)