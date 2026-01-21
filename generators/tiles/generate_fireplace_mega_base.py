import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
from patterns import csg_patterns
import palette

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

def generate_fireplace_mega_base():
    name = "fireplace_mega_base"
    instructions = []
    
    # ---------------------------------------------------------
    # Coordinate System:
    # Asset Origin (0,0,0) corresponds to the Center of the Primary Tile (NW cell).
    # 2x2 Block covers absolute area (0,0) to (64,64).
    # Primary Tile Center is at absolute (16, 16).
    #
    # Relative Bounds: X: -16 to 48, Y: -16 to 48.
    # ---------------------------------------------------------

    # 1. Floor: 4x 32x32 Tiles
    # Offsets relative to Primary Center (0,0)
    # NW: (0,0), NE: (32,0), SW: (0,32), SE: (32,32)
    floor_offsets = [
        [0, 0],   # NW (Primary)
        [32, 0],  # NE
        [0, 32],  # SW
        [32, 32]  # SE
    ]
    
    for off in floor_offsets:
        ox, oy = off
        # Base Layer (Dark Grout)
        instructions.append({
            "op": "add",
            "pos": [-16 + ox, -16 + oy, 0],
            "size": [32, 32, 1],
            "color": palette.WOOD_DARK
        })
        
        # Surface Layer (Solid Wood, No Planks)
        # Inset by 1 to create grout line effect
        instructions.append({
            "op": "add",
            "pos": [-15 + ox, -15 + oy, 1],
            "size": [30, 30, 1],
            "color": palette.WOOD_BROWN
        })

    # 2. Fireplace (Imported)
    fp_path = os.path.join(os.path.dirname(__file__), '../../csg/stone_fireplace.json')
    if os.path.exists(fp_path):
        with open(fp_path, 'r') as f:
            fp_data = json.load(f)
            fp_instr = fp_data.get('instructions', [])
            
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
