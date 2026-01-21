import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns
from patterns.micro_props import make_window
import math

def generate_wall_north_window_32():
    instructions = []
    
    # --- 1. Floor Generation (Base 32x32) ---
    f_size = 32
    half_size = f_size // 2
    
    instructions.append({
        "op": "add",
        "pos": [-half_size, -half_size, 0],
        "size": [f_size, f_size, 1],
        "color": palette.WOOD_DARK
    })
    
    instructions.extend(csg_patterns.create_plank_volume(
        start_pos=(-half_size + 1, -half_size + 1, 1),
        size=(f_size - 2, f_size - 2, 1),
        plank_size=(16, 5, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y',
        paint_mortar=True,
        mortar_color=palette.WOOD_DARK
    ))

    # --- 2. Wall Generation (North Edge) ---
    w_len = 32
    w_h = 96
    wall_back_y = -16
    beam_thick = 12
    plaster_thick = 4
    
    # Window cutout
    win_w = 24
    win_h = 32
    win_z_base = 45
    win_x_start = (w_len - win_w) // 2
    win_x_end = win_x_start + win_w
    
    # 2.1 Plaster
    patch_size = 4
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            if x >= win_x_start and x < win_x_end and z >= win_z_base and z < win_z_base + win_h:
                continue
            noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            instructions.append({
                "op": "add",
                "pos": [x - half_size, wall_back_y, z],
                "size": [min(patch_size, w_len - x), plaster_thick, min(patch_size, w_h - z)],
                "color": shade
            })
            
    # 2.2 Stone Wainscoting
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back_y, 0),
        size=(w_len, plaster_thick, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 Beams
    for z in [0, 40, w_h - 6]:
        instructions.append({
            "op": "add",
            "pos": [-half_size, wall_back_y, z],
            "size": [w_len, beam_thick, 6],
            "color": palette.WOOD_DARK
        })
        
    for x_rel in [0, win_x_start, win_x_end - 4, w_len - 6]:
        instructions.append({
            "op": "add",
            "pos": [x_rel - half_size, wall_back_y, 0],
            "size": [4 if x_rel in [win_x_start, win_x_end-4] else 6, beam_thick, w_h if x_rel in [0, w_len-6] else win_h + 10], # Vertical beams around window
            "color": palette.WOOD_DARK
        })

    # --- 3. The Window ---
    win_b = make_window(win_w, win_h)
    win_instr = win_b.get_instructions()
    # make_window is centered on X, Y, Z starts at 0.
    # We need it at Y=wall_back_y + plaster_thick, Z=win_z_base
    for inst in win_instr:
        inst['pos'][1] += (wall_back_y + plaster_thick)
        inst['pos'][2] += win_z_base
        instructions.append(inst)

    data = {
        "name": "wall_north_window_32",
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "south": {"pos": [0, 16, 0]},
            "east": {"pos": [16, 0, 0]},
            "west": {"pos": [-16, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/wall_north_window_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_wall_north_window_32()
