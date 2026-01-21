import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

def generate_wall_north_32():
    instructions = []
    
    # --- 1. Floor Generation (Base 32x32) ---
    instructions.extend(floor_wood_plain.get_instructions(32, 32))

    # --- 2. Wall Generation (North Edge) ---
    f_size = 32
    half_size = f_size // 2 # 16
    w_len = 32
    w_h = 96
    
    # Y-Coordinates
    wall_back_y = -16
    wall_front_y = -4
    wall_thickness = 12
    
    plaster_thickness = 4
    
    # 2.1 Plaster (Exterior Panel)
    patch_size = 4
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size): # Start at 40 (wainscoting height)
            noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_w = min(patch_size, w_len - x)
            p_h = min(patch_size, w_h - z)
            
            # X pos needs to be shifted by -half_size
            global_x = (x - half_size)
            
            instructions.append({
                "op": "add",
                "pos": [global_x, wall_back_y, z],
                "size": [p_w, plaster_thickness, p_h],
                "color": shade
            })
            
    # 2.2 Stone Wainscoting
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back_y, 0),
        size=(w_len, plaster_thickness, 40), # mid_z = 40
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 Beams (Frame)
    beam_thick = 12
    beam_h_dim = 6
    
    for z in [0, 40, w_h - beam_h_dim]:
        instructions.append({
            "op": "add",
            "pos": [-half_size, wall_back_y, z],
            "size": [w_len, beam_thick, beam_h_dim],
            "color": palette.WOOD_DARK
        })
        
    v_beam_w = 6
    
    for x_rel in [0, w_len - v_beam_w]:
        instructions.append({
            "op": "add",
            "pos": [x_rel - half_size, wall_back_y, 0],
            "size": [v_beam_w, beam_thick, w_h],
            "color": palette.WOOD_DARK
        })

    # Output
    data = {
        "name": "wall_north_32",
        "asset_tags": ["structure", "wall", "north", "base"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "south": {"pos": [0, 16, 0]},
            "east": {"pos": [16, 0, 0]},
            "west": {"pos": [-16, 0, 0]},
            "wall_face": {"pos": [0, -4, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/wall_north_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_wall_north_32()
