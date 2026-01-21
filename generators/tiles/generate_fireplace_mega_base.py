import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
from generators.floors import floor_wood_plain
import palette

import math

def offset_instructions(instr_list, offset):
    new_list = []
    ox, oy, oz = offset
    for item in instr_list:
        new_item = item.copy()
        if 'pos' in new_item:
            px, py, pz = new_item['pos']
            new_item['pos'] = [px + ox, py + oy, pz + oz]
        new_list.append(new_item)
    return new_list

def rotate_instructions(instr_list, angle_degrees):
    """
    Rotates instructions around the Z axis (XY plane).
    angle_degrees: 90, 180, 270 (Counter-Clockwise)
    """
    rad = math.radians(angle_degrees)
    cos_a = int(round(math.cos(rad))) # forcing int for 90/180/270 cleanliness
    sin_a = int(round(math.sin(rad)))
    
    new_list = []
    for item in instr_list:
        new_item = item.copy()
        if 'pos' in new_item and 'size' in new_item:
            x, y, z = new_item['pos']
            w, h, d = new_item['size']
            
            # Calculate the 4 corners of the base rectangle
            corners = [
                (x, y),
                (x + w, y),
                (x, y + h),
                (x + w, y + h)
            ]
            
            # Rotate all corners
            rotated_corners = []
            for cx, cy in corners:
                rx = cx * cos_a - cy * sin_a
                ry = cx * sin_a + cy * cos_a
                rotated_corners.append((rx, ry))
                
            # Find new min corner
            min_x = min(c[0] for c in rotated_corners)
            min_y = min(c[1] for c in rotated_corners)
            
            new_item['pos'] = [min_x, min_y, z]
            
            # Swap dimensions if 90 or 270
            if abs(angle_degrees % 180) == 90:
                new_item['size'] = [h, w, d]
                
        elif 'pos' in new_item:
             # Point rotation (for things without size, if any)
            x, y, z = new_item['pos']
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + cy * cos_a # Typos in original thought, fixing here: y*cos_a
            # Wait, correcting point rotation logic just in case
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            new_item['pos'] = [rx, ry, z]

        new_list.append(new_item)
    return new_list

def generate_fireplace_mega_base():
    name = "fireplace_mega_base"
    instructions = []
    
    # 1. Floor: 4x 32x32 Tiles
    floor_offsets = [
        [0, 0],   # NW (Primary)
        [32, 0],  # NE
        [0, 32],  # SW
        [32, 32]  # SE
    ]
    
    for off in floor_offsets:
        ox, oy = off
        # Generate generic floor
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        # Offset it to the quadrant
        # Note: floor_wood_plain is centered at 0,0.
        # But our quadrant centers are at -16+16=0 relative?
        # My previous logic had offset [-16+ox, -16+oy].
        # floor_wood_plain uses [-width//2, ...].
        # If width=32, pos is [-16, -16].
        # So we just need to ADD [ox, oy, 0] to the floor instructions.
        floor_instr = offset_instructions(floor_instr, [ox, oy, 0])
        instructions.extend(floor_instr)

    # 2. Fireplace (Imported)
    fp_path = os.path.join(os.path.dirname(__file__), '../../csg/stone_fireplace.json')
    if os.path.exists(fp_path):
        with open(fp_path, 'r') as f:
            fp_data = json.load(f)
            fp_instr = fp_data.get('instructions', [])
            
            # Rotate 180 degrees (facing South)
            fp_instr = rotate_instructions(fp_instr, 180)
            
            # Position: 
            # X: Centered in 2x2 block -> Absolute 32. Relative: 32 - 16 = 16.
            # Y: Backed against North Wall -> Absolute 0. Relative: 0 - 16 = -16.
            # Fireplace depth ~20. Center ~10.
            # So Center Y should be around -16 + 10 = -6.
            fp_instr = offset_instructions(fp_instr, [16, -6, 0])
            instructions.extend(fp_instr)
    
    # 3. North Wall (Timber segments flanking fireplace)
    # Fireplace width ~46.
    # Total Width 64. Bounds: Relative -16 to 48.
    # Center X=16. Fireplace spans 16-23 to 16+23 -> -7 to 39.
    # Left Gap: -16 to -7 (Width 9).
    # Right Gap: 39 to 48 (Width 9).
    
    # Left Wall
    instructions.append({
        "op": "add",
        "pos": [-16, -16, 0], # Back-Left corner relative
        "size": [9, 4, 32], 
        "color": palette.WOOD_DARK
    })
    
    # Right Wall
    instructions.append({
        "op": "add",
        "pos": [39, -16, 0], # Right side of fireplace
        "size": [9, 4, 32],
        "color": palette.WOOD_DARK
    })

    # Save
    data = {
        "name": name,
        "asset_tags": ["base", "mega", "fireplace"],
        "instructions": instructions,
        "snap_points": {
            # Center of the 2x2 block is (16, 16) relative
            "hearth_rug": {"pos": [16, 16, 0]},
            
            # Chairs flanking the rug
            # Left Chair: At X=0 (inside left tile), Y=24 (forward)
            "chair_left": {"pos": [0, 24, 0]}, 
            
            # Right Chair: At X=32 (inside right tile), Y=24
            "chair_right": {"pos": [32, 24, 0]},
            
            "mantle_left": {"pos": [8, -8, 20]},
            "mantle_right": {"pos": [24, -8, 20]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), f"../../csg/{name}.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_fireplace_mega_base()
