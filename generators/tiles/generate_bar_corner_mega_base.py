import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

# Use Local Constants if palette missing specific ones
METAL_DARK = 47
METAL_RUST = 48
WOOD_DARK = 2
WOOD_LIGHT = 3

def generate_bar_corner_mega_base():
    instructions = []
    
    # Dimensions: 4 tiles wide (X=128), 2 tiles deep (Z=64)
    width = 128
    depth = 64
    
    # 1. Floor (4x2 tiles) - Explicit XZ generation
    for x in range(0, 4):
        for z in range(0, 2):
            # Center of the 32x32 sub-tile
            cx = (x * 32) + 16
            cz = (z * 32) + 16
            
            # Base Layer (Dark Grout) - Size 32x1x32
            instructions.append({
                "op": "add",
                "pos": [cx - 16, -1, cz - 16], # Top-Left corner of tile
                "size": [32, 1, 32],
                "color": palette.WOOD_DARK
            })
            
            # Surface Layer (Wood) - Size 30x1x30 (Inset 1)
            instructions.append({
                "op": "add",
                "pos": [cx - 15, 0, cz - 15],
                "size": [30, 1, 30],
                "color": palette.WOOD_BROWN
            })

    # 2. Walls (Wainscoting Only)
    # North Wall (along X axis, at Z=0)
    # West Wall (along Z axis, at X=0)
    
    wall_h = 96
    wall_thick = 12
    plaster_thick = 4
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]

    # 2.1 North Wall
    # Wainscoting (Y=0..40)
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(0, 0, 0), # x, y, z
        size=(width, 40, plaster_thick), # w, h, d
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
        
    # 2.2 West Wall (at X=0)
    # Wainscoting
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(0, 0, 0),
        size=(plaster_thick, 40, depth),
        brick_size=(4, 4, 8),
        color=stone_mix,
        mortar=1
    ))

    # 3. Wine Rack (Against North Wall)
    # Z-pos: 8 (just in front of wall beam)
    # X-Range: 16 to 112 (Centered-ish)
    # Height: 0 to 80
    
    rack_z = 8
    rack_x_start = 32 # Leave space for West corner
    rack_w = 80
    rack_h = 70
    rack_depth = 12
    
    # Vertical Supports
    for x in [rack_x_start, rack_x_start + 40, rack_x_start + 80]:
        instructions.append({
            "op": "add",
            "pos": [x, 0, rack_z],
            "size": [4, rack_h, rack_depth],
            "color": palette.WOOD_DARK
        })
        
    # Horizontal Shelves
    for y in range(10, rack_h, 15):
        instructions.append({
            "op": "add",
            "pos": [rack_x_start, y, rack_z],
            "size": [rack_w + 4, 2, rack_depth],
            "color": palette.WOOD_BROWN
        })
        # Bottles!
        for bx in range(rack_x_start + 4, rack_x_start + rack_w, 6):
            instructions.append({
                "op": "add",
                "pos": [bx, y+2, rack_z + 4],
                "size": [4, 8, 4],
                "color": 41 # "Wine" color?
            })
            # Neck
            instructions.append({
                "op": "add",
                "pos": [bx+1, y+10, rack_z + 5],
                "size": [2, 3, 2],
                "color": 41
            })

    # 4. Bar Counter (L-Shape)
    # Bartender Space: Z=0 to 32.
    # Counter Z: 32.
    # Counter Width: 16.
    
    cnt_z = 32
    cnt_h = 24 # Waist high
    cnt_d = 16
    
    # Main Run (East-West)
    # Starts from X=32 (Corner) to X=120
    main_run_x = 32
    main_run_len = width - 40
    
    # Counter Body
    instructions.append({
        "op": "add",
        "pos": [main_run_x, 0, cnt_z],
        "size": [main_run_len, cnt_h, cnt_d],
        "color": palette.WOOD_DARK
    })
    # Counter Top
    instructions.append({
        "op": "add",
        "pos": [main_run_x - 2, cnt_h, cnt_z - 2],
        "size": [main_run_len + 4, 2, cnt_d + 4],
        "color": palette.WOOD_LIGHT
    })
    
    # Return (North-South)
    # At X=32, running from Z=0 to Z=32
    # Connecting to West Wall? Or free standing?
    # If West wall is at X=0, and Counter starts at X=32, there is a gap (pass through?).
    # Let's make the return connect to the West Wall?
    # Or leave a gap for bartender entry?
    # Bartender entry usually at the end.
    # Let's put a "Lift gate" or gap at the West side.
    # So Return starts at X=32, Z=16..32?
    
    return_x = 32
    return_z_start = 16
    return_len_z = 16 # up to 32
    
    instructions.append({
        "op": "add",
        "pos": [return_x, 0, return_z_start],
        "size": [cnt_d, cnt_h, return_len_z],
        "color": palette.WOOD_DARK
    })
    # Top
    instructions.append({
        "op": "add",
        "pos": [return_x - 2, cnt_h, return_z_start - 2],
        "size": [cnt_d + 4, 2, return_len_z + 4],
        "color": palette.WOOD_LIGHT
    })

    # Output
    data = {
        "name": "bar_corner_mega_base",
        "asset_tags": ["structure", "bar", "mega", "tavern"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "mug_spot": {"pos": [64, 26, 40]},
            "candle_spot": {"pos": [96, 26, 40]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/bar_corner_mega_base.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_bar_corner_mega_base()