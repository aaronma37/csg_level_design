import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

def generate_tavern_wall_mega_plaster_3x1():
    instructions = []
    
    # Dimensions
    w_len = 96
    w_h = 96
    
    # Y-Coordinates
    wall_back_y = -16
    plaster_thickness = 4
    
    beam_thick = 12
    start_x = -48
    
    # --- 1. Floor Generation (3x 32x32) ---
    for x_off in [-32, 0, 32]:
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        for item in floor_instr:
            if 'pos' in item:
                item['pos'][0] += x_off
        instructions.extend(floor_instr)

    # --- 2. Wall Generation (Full 96 width) ---
    
    # 2.1 Plaster Panels (Full)
    patch_size = 4
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            true_x = x + start_x
            noise_val = math.sin(true_x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            cur_w = min(patch_size, w_len - x)
            cur_h = min(patch_size, w_h - z)
            
            instructions.append({
                "op": "add",
                "pos": [true_x, wall_back_y, z],
                "size": [cur_w, plaster_thickness, cur_h],
                "color": shade
            })
            
    # 2.2 Stone Wainscoting
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(start_x, wall_back_y, 0),
        size=(w_len, plaster_thickness, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 Horizontal Beams (Bottom, Middle, Top)
    # No Vertical Beams requested.
    beam_h_dim = 6
    for z in [0, 40, w_h - beam_h_dim]:
         instructions.append({
            "op": "add",
            "pos": [start_x, wall_back_y, z],
            "size": [w_len, beam_thick, beam_h_dim],
            "color": palette.WOOD_DARK
        })

    # Output
    data = {
        "name": "tavern_wall_mega_plaster_3x1",
        "asset_tags": ["structure", "wall", "mega", "tavern", "plaster"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/tavern_wall_mega_plaster_3x1.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_tavern_wall_mega_plaster_3x1()
