import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

# Local Palette Constants
METAL_DARK = 47
METAL_GOLD = 43
METAL_RUST = 48

def generate_tavern_window_mega_3x1():
    instructions = []
    
    # Dimensions
    w_len = 96
    w_h = 96
    
    # Y-Coordinates
    wall_back_y = -16
    wall_thickness = 12
    plaster_thickness = 4
    
    beam_thick = 12
    v_beam_w = 8 # End posts
    
    start_x = -48
    
    # Window Definitions
    win_w = 40
    win_h = 40
    win_y_start = 44 # Just above the wainscoting (40) + beam (6)?
                     # Actually mid-beam is at 40. Let's put window above the mid-beam.
                     # Mid beam is at Z=40, height 6. So top is 46.
    win_y_start = 48
    
    win_half_w = win_w // 2
    
    # --- 1. Floor Generation (3x 32x32) ---
    for x_off in [-32, 0, 32]:
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        for item in floor_instr:
            if 'pos' in item:
                item['pos'][0] += x_off
        instructions.extend(floor_instr)

    # --- 2. Wall Generation (Full width minus window hole) ---
    # We can build this as:
    # A. Full Wainscoting (0-40)
    # B. Full Mid Beam (40-46)
    # C. Full Top Beam (90-96)
    # D. Plaster: Left Side, Right Side, Top Side, Bottom Side? 
    #    Actually easier to do Left Panel and Right Panel, and Top/Bottom fillers.
    
    # 2.1 Stone Wainscoting (Full Width)
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(start_x, wall_back_y, 0),
        size=(w_len, plaster_thickness, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.2 Horizontal Beams
    beam_h_dim = 6
    # Bottom (0), Middle (40), Top (90)
    for z in [0, 40, w_h - beam_h_dim]:
         instructions.append({
            "op": "add",
            "pos": [start_x, wall_back_y, z],
            "size": [w_len, beam_thick, beam_h_dim],
            "color": palette.WOOD_DARK
        })

    # 2.3 Plaster Panels (Upper Wall 46 to 90)
    # Window Hole: x = [-20, 20], z = [48, 88] (height 40)
    
    plaster_z_start = 46
    plaster_z_end = 90
    
    # Left Panel: -48 to -20
    # Right Panel: 20 to 48
    # Top Strip: -20 to 20 (above window, z=88 to 90? Window is 48+40=88. So 2 units gap)
    # Bottom Strip: -20 to 20 (below window, z=46 to 48)
    
    panels = [
        {"x": start_x, "w": 28, "z": 46, "h": 44}, # Left (-48 to -20)
        {"x": 20, "w": 28, "z": 46, "h": 44},      # Right (20 to 48)
        {"x": -20, "w": 40, "z": 88, "h": 2},      # Top
        {"x": -20, "w": 40, "z": 46, "h": 2},      # Bottom
    ]
    
    patch_size = 4
    for p in panels:
        px_start = p["x"]
        px_end = p["x"] + p["w"]
        pz_start = p["z"]
        pz_end = p["z"] + p["h"]
        
        for x in range(px_start, px_end, patch_size):
            for z in range(pz_start, pz_end, patch_size):
                noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
                shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
                
                cur_w = min(patch_size, px_end - x)
                cur_h = min(patch_size, pz_end - z)
                
                instructions.append({
                    "op": "add",
                    "pos": [x, wall_back_y, z],
                    "size": [cur_w, plaster_thickness, cur_h],
                    "color": shade
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

    # --- 4. Window Frame & Shelf ---
    
    # Frame (Inset)
    frame_thick = 2
    frame_depth = 8 # Slightly less than beam
    
    # Top/Bottom/Left/Right Frame parts
    # Left
    instructions.append({
        "op": "add",
        "pos": [-20, wall_back_y + 2, 48],
        "size": [2, frame_depth, 40],
        "color": palette.WOOD_BROWN
    })
    # Right
    instructions.append({
        "op": "add",
        "pos": [18, wall_back_y + 2, 48],
        "size": [2, frame_depth, 40],
        "color": palette.WOOD_BROWN
    })
    # Top
    instructions.append({
        "op": "add",
        "pos": [-20, wall_back_y + 2, 86],
        "size": [40, frame_depth, 2],
        "color": palette.WOOD_BROWN
    })
    # Bottom
    instructions.append({
        "op": "add",
        "pos": [-20, wall_back_y + 2, 48],
        "size": [40, frame_depth, 2],
        "color": palette.WOOD_BROWN
    })
    
    # Crossbars (Mullions)
    # Vertical Mid
    instructions.append({
        "op": "add",
        "pos": [-1, wall_back_y + 4, 48],
        "size": [2, 4, 40],
        "color": palette.WOOD_BROWN
    })
    # Horizontal Mid
    instructions.append({
        "op": "add",
        "pos": [-20, wall_back_y + 4, 67],
        "size": [40, 4, 2],
        "color": palette.WOOD_BROWN
    })
    
    # Glass (Blue-ish plane in middle)
    instructions.append({
        "op": "add",
        "pos": [-18, wall_back_y + 5, 50],
        "size": [36, 2, 36],
        "color": palette.WINDOW_GLOW
    })
    
    # --- 5. The Shelf (Sill) ---
    # Under the window (Z=46..48 range, or attached to the mid beam at 40?)
    # User said "under it".
    # Let's put it at the bottom of the window frame, extending out.
    # Window bottom is Z=48.
    # Shelf should be at Z=46 (Top of mid beam) but sticking out further.
    
    shelf_depth = 12 # Sticks out 12 units
    shelf_width = 44 # Slightly wider than window
    shelf_thick = 4
    shelf_y = wall_back_y + beam_thick # Flush with front of beam?
    # Actually, let's make it sit ON the mid beam (Z=40..46) and stick out.
    
    # Mid beam front is at wall_back_y + 12 = -4.
    # Shelf starts at -10 and goes to +2 ?
    
    instructions.append({
        "op": "add",
        "pos": [-22, wall_back_y + beam_thick, 44], # Z=44, so slightly below window
        "size": [44, 8, 4], # Stick out 8 units
        "color": palette.WOOD_LIGHT
    })
    
    # Brackets for shelf
    instructions.append({
        "op": "add",
        "pos": [-16, wall_back_y + beam_thick, 40],
        "size": [4, 4, 4], # Simple wedge placeholder
        "color": palette.WOOD_DARK
    })
    instructions.append({
        "op": "add",
        "pos": [12, wall_back_y + beam_thick, 40],
        "size": [4, 4, 4],
        "color": palette.WOOD_DARK
    })

    # Output
    data = {
        "name": "tavern_window_mega_3x1",
        "asset_tags": ["structure", "wall", "window", "mega", "tavern"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "shelf_left": {"pos": [-10, wall_back_y + beam_thick + 4, 48]},
            "shelf_right": {"pos": [10, wall_back_y + beam_thick + 4, 48]},
            "shelf_center": {"pos": [0, wall_back_y + beam_thick + 4, 48]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/tavern_window_mega_3x1.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_tavern_window_mega_3x1()
