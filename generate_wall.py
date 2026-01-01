import json
import palette
import csg_patterns
import random
import math

def generate_wall():
    random.seed(42)
    instructions = []
    
    # Dimensions
    w_len = 256
    w_h = 140
    mid_z = 46
    
    # Beams: Thinner but protrude more
    beam_thick = 12 # Protrude more (depth)
    beam_h_dim = 6  # Thinner cross-section
    v_beam_w_dim = 6
    
    plaster_thick = 4
    # Set plaster/bricks at the BACK of the beams
    back_y = beam_thick - plaster_thick
    
    # 1. Main Plaster Surface (Upper Part)
    print("Generating subtle noisy plaster...")
    # Smaller patches for less blockiness
    patch_size = 4 
    
    for x in range(0, w_len, patch_size):
        for z in range(mid_z, w_h, patch_size):
            # Use lower frequency for noise, but smaller patches
            noise_val = math.sin(x * 0.03) + math.cos(z * 0.03) + random.uniform(-0.2, 0.2)
            
            if noise_val < -0.3:
                shade = palette.BEIGE_DARK
            elif noise_val < 0.3:
                shade = palette.BEIGE_MEDIUM
            else:
                shade = palette.BEIGE_LIGHT
                
            p_w = min(patch_size, w_len - x)
            p_h = min(patch_size, w_h - z)
            
            instructions.append({
                "op": "add",
                "pos": [x, back_y, z],
                "size": [p_w, plaster_thick, p_h],
                "color": shade
            })
    
    # 2. Stone Brick Surface (Lower Part) - Now "Castle Stone"
    print("Generating castle stone wainscoting...")
    stone_mix = [palette.STONE_LIGHT, palette.STONE_LIGHT, palette.STONE_DARK]
    
    lower_bricks = csg_patterns.create_brick_volume(
        start_pos=(0, back_y, 0),
        size=(w_len, plaster_thick, mid_z),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1,
        randomize_layout=True
    )
    instructions.extend(lower_bricks)
    
    # 3. Horizontal Beams
    # Bottom
    instructions.append({
        "op": "add",
        "pos": [0, 0, 0],
        "size": [w_len, beam_thick, beam_h_dim],
        "color": palette.WOOD_DARK
    })
    
    # Middle
    instructions.append({
        "op": "add",
        "pos": [0, 0, mid_z],
        "size": [w_len, beam_thick, beam_h_dim],
        "color": palette.WOOD_DARK
    })
    
    # Top
    instructions.append({
        "op": "add",
        "pos": [0, 0, w_h - beam_h_dim],
        "size": [w_len, beam_thick, beam_h_dim],
        "color": palette.WOOD_DARK
    })
    
    # 4. Vertical Beams
    for x in [0, 64, 128, 192, w_len - v_beam_w_dim]:
        instructions.append({
            "op": "add",
            "pos": [x, 0, 0],
            "size": [v_beam_w_dim, beam_thick, w_h],
            "color": palette.WOOD_DARK
        })
        
    data = {
        "name": "timber_wall",
        "instructions": instructions
    }
    
    with open("timber_wall.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_wall()