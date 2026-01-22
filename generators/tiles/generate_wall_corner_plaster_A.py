import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

def generate_wall_corner_plaster_A():
    instructions = []
    
    # 1. Floor Generation
    instructions.extend(floor_wood_plain.get_instructions(32, 32))

    # Dimensions
    w_len = 32
    w_h = 96
    half_size = 16
    wall_back = -16
    
    plaster_thick = 4
    patch_size = 4
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    beam_thick = 12
    
    # --- North Wall (Along X) ---
    # Global X from -16 to 16. Noise Offset: -16.
    
    # North Plaster
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            true_x = -16 + x
            noise_val = math.sin(true_x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_w = min(patch_size, w_len - x)
            p_h = min(patch_size, w_h - z)
            
            instructions.append({
                "op": "add",
                "pos": [x - half_size, wall_back, z],
                "size": [p_w, plaster_thick, p_h],
                "color": shade
            })
            
    # North Wainscoting
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back, 0),
        size=(w_len, plaster_thick, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # North Beams
    for z in [0, 40, w_h - 6]:
        instructions.append({
            "op": "add",
            "pos": [-half_size, wall_back, z],
            "size": [w_len, beam_thick, 6],
            "color": palette.WOOD_DARK
        })
        
    # Corner Post (Shared)
    instructions.append({
        "op": "add",
        "pos": [-half_size, wall_back, 0],
        "size": [8, beam_thick, w_h],
        "color": palette.WOOD_DARK
    })

    # --- West Wall (Along Y) ---
    # Global Y from -16 to 16. Wall is at X = -16.
    
    wall_back_x = -16
    
    # West Plaster
    for y in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            true_y = -16 + y
            noise_val = math.sin(true_y * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_d = min(patch_size, w_len - y)
            p_h = min(patch_size, w_h - z)
            
            instructions.append({
                "op": "add",
                "pos": [wall_back_x, y - half_size, z],
                "size": [plaster_thick, p_d, p_h],
                "color": shade
            })
            
    # West Wainscoting (Rotated)
    bricks_west = csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back_x, 0),
        size=(w_len, plaster_thick, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    )
    
    for instr in bricks_west:
        x, y, z = instr['pos']
        w, d, h = instr['size']
        # Swap X/Y in pos and size to rotate 90 degrees around Z axis (conceptually)
        # We map the "North Wall" shape onto the "West Wall" position.
        # North Wall: y is fixed (-16). X varies.
        # West Wall: x is fixed (-16). Y varies.
        instr['pos'] = [y, x, z]
        instr['size'] = [d, w, h]
        instructions.append(instr)
        
    # West Beams
    for z in [0, 40, w_h - 6]:
        instructions.append({
            "op": "add",
            "pos": [wall_back_x, -half_size, z],
            "size": [beam_thick, w_len, 6],
            "color": palette.WOOD_DARK
        })
        
    # Output
    data = {
        "name": "wall_corner_plaster_A",
        "asset_tags": ["structure", "wall", "corner", "plaster", "base"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "west": {"pos": [-16, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/wall_corner_plaster_A.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_wall_corner_plaster_A()
