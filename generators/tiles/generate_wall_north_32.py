import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns
import math

def generate_wall_north_32():
    instructions = []
    
    # --- 1. Floor Generation (Base 32x32) ---
    # Based on floor_bevel_32
    f_size = 32
    half_size = f_size // 2 # 16
    
    # Base "Grout" Layer
    instructions.append({
        "op": "add",
        "pos": [-half_size, -half_size, 0],
        "size": [f_size, f_size, 1],
        "color": palette.WOOD_DARK
    })
    
    # Planks Layer
    # We leave the space under the wall mostly intact or cover it?
    # The wall is at Y = -16 to -4. 
    # Planks normally go -15 to +15 (with 1 unit margin).
    # Let's generate full floor, the wall will overwrite/intersect.
    plank_area_size = f_size - 2
    start_pos = (-half_size + 1, -half_size + 1, 1)
    
    instructions.extend(csg_patterns.create_plank_volume(
        start_pos=start_pos,
        size=(plank_area_size, plank_area_size, 1),
        plank_size=(16, 5, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y',
        paint_mortar=True,
        mortar_color=palette.WOOD_DARK
    ))

    # --- 2. Wall Generation (North Edge) ---
    # Original Wall: X[-16, 16], Y[0, 12], Z[0, 96]
    # Plaster (Back): Y[8, 12]
    # Beams: Y[0, 12]
    # Target: North Wall (Back flush with -16). Interior facing 0.
    # New Y Range: [-16, -4]
    # Plaster (Back/Exterior): [-16, -12] (Flush with edge)
    # Beams (Interior): [-16, -4]
    
    w_len = 32
    w_h = 96
    
    # Y-Coordinates
    wall_back_y = -16
    wall_front_y = -4
    wall_thickness = 12
    
    plaster_thickness = 4
    # Plaster sits at the back (most negative Y? No, "Back" in original was +Y relative to front)
    # Here "Back" is -16. "Front" is -4.
    # We want Plaster at -16 to -12.
    
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
            
    # 2.2 Stone Wainscoting (Bottom Exterior/Interior?)
    # Original: Y[back_y, back_y+thick] -> Y[8, 12].
    # We want it at [-16, -12].
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    # We generate bricks at origin, then translate?
    # Or generate in place. csg_patterns.create_brick_volume takes start_pos.
    
    # Note: Wainscoting usually is visible on the "Inside" too? 
    # Original code: `pos: [-half_w, back_y, 0]`. size `mid_z` height.
    # This implies Wainscoting was only on the "Back" (Plaster) layer.
    # The Beams covered the front.
    # So the "Inside" (Recessed) part was empty?
    # Let's replicate original look first: Panel is at back.
    
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_size, wall_back_y, 0),
        size=(w_len, plaster_thickness, 40), # mid_z = 40
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 Beams (Frame)
    # Horizontal Beams: Full Thickness [-16, -4]
    # Z-levels: 0, 40, 90
    beam_thick = 12
    beam_h_dim = 6
    
    for z in [0, 40, w_h - beam_h_dim]:
        instructions.append({
            "op": "add",
            "pos": [-half_size, wall_back_y, z],
            "size": [w_len, beam_thick, beam_h_dim],
            "color": palette.WOOD_DARK
        })
        
    # Vertical Beams: Full Thickness [-16, -4]
    # X-levels: 0, 26 (relative to start). 
    # Original: x in [0, w_len - 6].
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
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "south": {"pos": [0, 16, 0]},
            "east": {"pos": [16, 0, 0]},
            "west": {"pos": [-16, 0, 0]},
            # Add wall specific snaps?
            "wall_face": {"pos": [0, -4, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/wall_north_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_wall_north_32()
