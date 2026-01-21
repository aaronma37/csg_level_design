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
    
    # 1. Floor (64x32)
    # Centered at X=16, Y=0 (relative to Tile Origin 0,0)
    # Range X: -16 to 48. Range Y: -16 to 16.
    
    # Base Layer (Dark)
    instructions.append({
        "op": "add",
        "pos": [-16, -16, 0],
        "size": [64, 32, 1],
        "color": palette.WOOD_DARK
    })
    
    # Planks
    planks = csg_patterns.create_plank_volume(
        start_pos=(-15, -15, 1),
        size=(62, 30, 1),
        plank_size=(16, 5, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y',
        paint_mortar=True,
        mortar_color=palette.WOOD_DARK
    )
    # Offset planks to match the base at X=16
    # create_plank_volume starts at start_pos. 
    # start_pos (-15) is relative to what? It's absolute coords.
    # If we want X range -15 to 47.
    # The function generates from start_pos.
    # So start_pos X should be -15.
    # But wait, create_plank_volume generates relative to 0? No, absolute.
    # The previous example used [-half_size + 1] which is -15 for size 32.
    # We want to start at -16 + 1 = -15.
    # And extend 62 units wide. -15 + 62 = 47. Correct.
    # But wait, we want the WHOLE THING shifted by +16 if we want the 2-tile center.
    # No, I decided the geometry should span -16 to 48.
    # So Start X = -16.
    # Base rect: [-16, -16, 0].
    # Planks start: [-15, -15, 1].
    instructions.extend(planks)

    # 2. Fireplace (Imported)
    fp_path = os.path.join(os.path.dirname(__file__), '../../csg/stone_fireplace.json')
    if os.path.exists(fp_path):
        with open(fp_path, 'r') as f:
            fp_data = json.load(f)
            fp_instr = fp_data.get('instructions', [])
            
            # Position: Center of the 2-tile block is X=16.
            # North Wall is Y=-16.
            # Fireplace depth is approx 20?
            # Let's center it at X=16, Y=-6 (so back is at -16).
            fp_instr = offset_instructions(fp_instr, [16, -6, 0])
            instructions.extend(fp_instr)
    else:
        print(f"Warning: {fp_path} not found.")

    # 3. Side Walls (Timber)
    # To cover the gaps to the left/right of the fireplace.
    # Fireplace width is approx 46.
    # Total width 64. Gap = 18. ~9 on each side.
    # Left Wall: X range -16 to -7?
    # Right Wall: X range 39 to 48?
    # Let's add simple blocks for now to fill the gap.
    
    # Left Wall Segment
    instructions.append({
        "op": "add",
        "pos": [-16, -16, 0], # Top Left
        "size": [10, 4, 32],  # 10 wide, 4 deep, 32 tall
        "color": palette.WOOD_DARK # Placeholder color/material
    })
    
    # Right Wall Segment
    instructions.append({
        "op": "add",
        "pos": [38, -16, 0], # Right side
        "size": [10, 4, 32],
        "color": palette.WOOD_DARK
    })

    # Save
    data = {
        "name": name,
        "asset_tags": ["base", "mega", "fireplace"],
        "instructions": instructions,
        "snap_points": {
            # Define snaps for props
            "hearth": {"pos": [16, 0, 0]},
            "hearth_rug": {"pos": [16, 16, 0]},
            "chair_left": {"pos": [-4, 8, 0]}, 
            "chair_right": {"pos": [36, 8, 0]},
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
