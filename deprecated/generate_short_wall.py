import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns
import random
import math

def generate_short_wall():
    # Exactly like timber_wall but only 64 units long
    w_len = 64
    w_h = 140
    mid_z = 46
    beam_thick = 12
    beam_h_dim = 6
    v_beam_w_dim = 6
    plaster_thick = 4
    back_y = beam_thick - plaster_thick
    
    instructions = []
    patch_size = 4 
    for x in range(0, w_len, patch_size):
        for z in range(mid_z, w_h, patch_size):
            noise_val = math.sin(x * 0.03) + math.cos(z * 0.03)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            instructions.append({
                "op": "add", "pos": [x, back_y, z], "size": [min(patch_size, w_len-x), plaster_thick, min(patch_size, w_h-z)], "color": shade
            })
    
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    lower_bricks = csg_patterns.create_brick_volume(
        start_pos=(0, back_y, 0), size=(w_len, plaster_thick, mid_z),
        brick_size=(8, 4, 4), color=stone_mix, mortar=1
    )
    instructions.extend(lower_bricks)
    
    # Beams
    for z in [0, mid_z, w_h - beam_h_dim]:
        instructions.append({"op": "add", "pos": [0, 0, z], "size": [w_len, beam_thick, beam_h_dim], "color": palette.WOOD_DARK})
    for x in [0, w_len - v_beam_w_dim]:
        instructions.append({"op": "add", "pos": [x, 0, 0], "size": [v_beam_w_dim, beam_thick, w_h], "color": palette.WOOD_DARK})
        
    data = {"name": "timber_wall_short", "instructions": instructions, 
            "snap_points": { "next_segment": {"pos": [64, 0, 0], "rot": 0}, "corner_turn": {"pos": [64, 0, 0], "rot": 90} }}
    
    with open("csg/timber_wall_short.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_short_wall()
