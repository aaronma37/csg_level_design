import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns
import random
import math

def generate_wall_32():
    # Adjusted for 32x32 Grid
    # Length: 32 units
    w_len = 32
    w_h = 96 # Reduced from 140
    mid_z = 40 # Reduced wainscoting slightly to proportion
    
    # Beam dimensions (keep consistent)
    beam_thick = 12
    beam_h_dim = 6
    v_beam_w_dim = 6
    plaster_thick = 4
    back_y = beam_thick - plaster_thick
    
    instructions = []
    
    # 1. Main Plaster Surface (Upper)
    patch_size = 4 
    for x in range(0, w_len, patch_size):
        for z in range(mid_z, w_h, patch_size):
            noise_val = math.sin(x * 0.05) + math.cos(z * 0.05) # Higher frequency for smaller area
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_w = min(patch_size, w_len - x)
            p_h = min(patch_size, w_h - z)
            instructions.append({
                "op": "add",
                "pos": [x, back_y, z],
                "size": [p_w, plaster_thick, p_h],
                "color": shade
            })
    
    # 2. Stone Wainscoting
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    lower_bricks = csg_patterns.create_brick_volume(
        start_pos=(0, back_y, 0),
        size=(w_len, plaster_thick, mid_z),
        brick_size=(8, 4, 4), 
        color=stone_mix, 
        mortar=1
    )
    instructions.extend(lower_bricks)
    
    # 3. Horizontal Beams (Top, Mid, Bottom)
    for z in [0, mid_z, w_h - beam_h_dim]:
        instructions.append({
            "op": "add", 
            "pos": [0, 0, z], 
            "size": [w_len, beam_thick, beam_h_dim], 
            "color": palette.WOOD_DARK
        })
        
    # 4. Vertical Beams
    # For a 32-wide segment, we definitely need pillars on both ends? 
    # Or just one end to avoid "double pillars" when tiling?
    # A standard "Modular" tile usually has pillars on BOTH ends if it's a discrete unit,
    # OR just left side.
    # If we put pillars on both 0 and 32 (actually 32-width), tiling them gives 2 pillars side-by-side (12 width total).
    # That looks okay for "Structural" feel.
    # Let's put pillars at 0 and w_len-beam_w.
    
    for x in [0, w_len - v_beam_w_dim]:
        instructions.append({
            "op": "add", 
            "pos": [x, 0, 0], 
            "size": [v_beam_w_dim, beam_thick, w_h], 
            "color": palette.WOOD_DARK
        })
        
    data = {
        "name": "timber_wall_32",
        "instructions": instructions
    }
    
    with open(os.path.join(os.path.dirname(__file__), "../csg/timber_wall_32.json"), "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_wall_32()
