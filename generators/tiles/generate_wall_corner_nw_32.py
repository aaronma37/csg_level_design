import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

def generate_wall_corner_nw_32():
    instructions = []
    
    # --- 1. Floor Generation ---
    instructions.extend(floor_wood_plain.get_instructions(32, 32))

    # --- 2. North Wall ---
    f_size = 32
    half_size = f_size // 2
    w_len = 32
    w_h = 96
    wall_back_y = -16
    beam_thick = 12
    plaster_thick = 4
    
    # 2.1 North Plaster
    patch_size = 4
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            instructions.append({
                "op": "add",
                "pos": [x - half_size, wall_back_y, z],
                "size": [min(patch_size, w_len - x), plaster_thick, min(patch_size, w_h - z)],
                "color": shade
            })
            
    # 2.2 North Stone Wainscoting
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back_y, 0),
        size=(w_len, plaster_thick, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 North Beams
    for z in [0, 40, w_h - 6]:
        instructions.append({
            "op": "add",
            "pos": [-half_size, wall_back_y, z],
            "size": [w_len, beam_thick, 6],
            "color": palette.WOOD_DARK
        })
        
    for x_rel in [0, w_len - 6]:
        instructions.append({
            "op": "add",
            "pos": [x_rel - half_size, wall_back_y, 0],
            "size": [6, beam_thick, w_h],
            "color": palette.WOOD_DARK
        })

    # --- 3. West Wall ---
    wall_back_x = -16
    
    # 3.1 West Plaster
    for y in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            noise_val = math.sin(y * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            instructions.append({
                "op": "add",
                "pos": [wall_back_x, y - half_size, z],
                "size": [plaster_thick, min(patch_size, w_len - y), min(patch_size, w_h - z)],
                "color": shade
            })
            
    # 3.2 West Stone Wainscoting
    for y in range(0, w_len, 8):
        for z in range(0, 40, 4):
            color = random.choice(stone_mix)
            instructions.append({
                "op": "add",
                "pos": [wall_back_x, y - half_size, z],
                "size": [plaster_thick, 8, 4],
                "color": color
            })
            
    # 3.3 West Beams
    for z in [0, 40, w_h - 6]:
        instructions.append({
            "op": "add",
            "pos": [wall_back_x, -half_size, z],
            "size": [beam_thick, w_len, 6],
            "color": palette.WOOD_DARK
        })
        
    for y_rel in [0, w_len - 6]:
        instructions.append({
            "op": "add",
            "pos": [wall_back_x, y_rel - half_size, 0],
            "size": [beam_thick, 6, w_h],
            "color": palette.WOOD_DARK
        })

    data = {
        "name": "wall_corner_nw_32",
        "asset_tags": ["structure", "wall", "corner", "north", "west", "base"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "west": {"pos": [-16, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/wall_corner_nw_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    import random
    random.seed(42)
    generate_wall_corner_nw_32()
