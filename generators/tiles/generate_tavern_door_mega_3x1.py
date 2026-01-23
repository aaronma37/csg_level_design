import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

# Local Palette Constants
METAL_DARK = 47 # Charcoal
METAL_GOLD = 43 # Fabric Gold
METAL_RUST = 48 # Fabric Maroon (Rust-like)

def generate_tavern_door_mega_3x1():
    instructions = []
    
    # Dimensions
    w_len = 96
    w_h = 96 # Standard wall height
    
    # Anchor at middle tile (Tile 1).
    # Tile 0 Center: -32
    # Tile 1 Center: 0
    # Tile 2 Center: 32
    # Total span: -48 to 48
    
    # Y-Coordinates
    wall_back_y = -16
    wall_thickness = 12 # Main beam thickness
    plaster_thickness = 4
    
    beam_thick = 12
    v_beam_w = 8 # End posts
    
    start_x = -48
    
    # Doorway definitions
    door_w = 40
    door_h = 70
    door_half_w = door_w // 2 # 20
    
    # Gaps for the door: -20 to 20
    # Left Wall: -48 to -20
    # Right Wall: 20 to 48
    
    # --- 1. Floor Generation (3x 32x32 Tiles) ---
    for x_off in [-32, 0, 32]:
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        for item in floor_instr:
            if 'pos' in item:
                item['pos'][0] += x_off
        instructions.extend(floor_instr)

    # --- 2. Wall Segments (Left and Right) ---
    
    segments = [
        {"start": -48, "end": -door_half_w}, # Left
        {"start": door_half_w, "end": 48}    # Right
    ]
    
    for seg in segments:
        s_start = seg["start"]
        s_end = seg["end"]
        s_width = s_end - s_start
        
        # 2.1 Stone Wainscoting (0 to 40)
        stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
        instructions.extend(csg_patterns.create_brick_volume(
            start_pos=(s_start, wall_back_y, 0),
            size=(s_width, plaster_thickness, 40),
            brick_size=(8, 4, 4),
            color=stone_mix,
            mortar=1
        ))
        
        # 2.2 Plaster (40 to 96)
        patch_size = 4
        for x in range(s_start, s_end, patch_size):
            for z in range(40, w_h, patch_size):
                noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
                shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
                
                p_w = min(patch_size, s_end - x)
                p_h = min(patch_size, w_h - z)
                
                instructions.append({
                    "op": "add",
                    "pos": [x, wall_back_y, z],
                    "size": [p_w, plaster_thickness, p_h],
                    "color": shade
                })
        
        # 2.3 Horizontal Beams (0, 40, 90)
        beam_h_dim = 6
        for z in [0, 40, w_h - beam_h_dim]:
             instructions.append({
                "op": "add",
                "pos": [s_start, wall_back_y, z],
                "size": [s_width, beam_thick, beam_h_dim],
                "color": palette.WOOD_DARK
            })

    # --- 3. Vertical Posts (Ends) ---
    # Left Post
    instructions.append({
        "op": "add",
        "pos": [start_x, wall_back_y, 0],
        "size": [v_beam_w, beam_thick, w_h],
        "color": palette.WOOD_DARK
    })
    
    # Right Post
    instructions.append({
        "op": "add",
        "pos": [48 - v_beam_w, wall_back_y, 0],
        "size": [v_beam_w, beam_thick, w_h],
        "color": palette.WOOD_DARK
    })

    # --- 3.5 Door Frame (Inner Posts) ---
    frame_w = 4
    # Left Inner Frame (-24 to -20)
    instructions.append({
        "op": "add",
        "pos": [-20 - frame_w, wall_back_y, 0],
        "size": [frame_w, beam_thick, door_h],
        "color": palette.WOOD_DARK
    })
    # Right Inner Frame (20 to 24)
    instructions.append({
        "op": "add",
        "pos": [20, wall_back_y, 0],
        "size": [frame_w, beam_thick, door_h],
        "color": palette.WOOD_DARK
    })

    
    # --- 4. Door Header (Above Door) ---
    # Lintel Beam
    lintel_thick = 8
    instructions.append({
        "op": "add",
        "pos": [-door_half_w, wall_back_y, door_h],
        "size": [door_w, beam_thick, lintel_thick],
        "color": palette.WOOD_DARK
    })
    
    # Plaster Filler above Lintel (78 to 96)
    # 70 + 8 = 78
    start_fill = door_h + lintel_thick
    fill_h = w_h - start_fill
    if fill_h > 0:
        instructions.append({
            "op": "add",
            "pos": [-door_half_w, wall_back_y, start_fill],
            "size": [door_w, plaster_thickness, fill_h],
            "color": palette.BEIGE_MEDIUM
        })
        # Top Beam across filler
        instructions.append({
            "op": "add",
            "pos": [-door_half_w, wall_back_y, w_h - 6],
            "size": [door_w, beam_thick, 6],
            "color": palette.WOOD_DARK
        })

    # --- 5. The Door ---
    # Centered in frame depth
    door_thick = 6
    door_y = wall_back_y + (beam_thick - door_thick) // 2 
    
    # Door Planks
    plank_w = 5
    door_start_x = -door_half_w + 2 # slight gap from frame
    door_actual_w = door_w - 4
    
    for x in range(0, door_actual_w, plank_w):
        cur_w = min(plank_w, door_actual_w - x)
        # Vary color slightly
        col = palette.WOOD_BROWN if (x // plank_w) % 2 == 0 else palette.WOOD_LIGHT
        
        instructions.append({
            "op": "add",
            "pos": [door_start_x + x, door_y, 0],
            "size": [cur_w, door_thick, door_h],
            "color": col
        })
        
    # Metal Bands / Bolts (Facing "Inside" / South / +Y)
    bolt_z_levels = [10, door_h - 10]
    band_height = 4
    
    for z in bolt_z_levels:
        # Band
        instructions.append({
            "op": "add",
            "pos": [door_start_x, door_y + door_thick, z], # Pop out towards +Y (Inside)
            "size": [door_actual_w, 1, band_height], # Thin band
            "color": METAL_RUST
        })
        # Bolts (Studs)
        for b_x in range(2, door_actual_w, 8):
             instructions.append({
                "op": "add",
                "pos": [door_start_x + b_x, door_y + door_thick + 1, z + 1], # Pop out more
                "size": [2, 1, 2],
                "color": METAL_DARK
            })

    # Door Knob (Facing "Inside")
    knob_z = 30
    knob_x = door_start_x + door_actual_w - 6 # Right side
    instructions.append({
        "op": "add",
        "pos": [knob_x, door_y + door_thick, knob_z],
        "size": [4, 3, 4],
        "color": METAL_GOLD
    })

    # Output
    data = {
        "name": "tavern_door_mega_3x1",
        "asset_tags": ["structure", "door", "mega", "tavern"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "left_post": {"pos": [start_x + v_beam_w/2, wall_back_y, 0]},
            "right_post": {"pos": [48 - v_beam_w/2, wall_back_y, 0]},
            "candle_left": {"pos": [-30, wall_back_y + beam_thick/2, 46]}, # Centered on beam, sitting on top
            "candle_right": {"pos": [30, wall_back_y + beam_thick/2, 46]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/tavern_door_mega_3x1.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_tavern_door_mega_3x1()