import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
import math

def generate_segment(name, width, height, depth, global_x_offset, total_width, tags):
    instructions = []
    
    half_w = width // 2
    half_d = depth // 2
    wall_back_y = -half_d
    
    # 1. Floor
    instructions.extend(floor_wood_plain.get_instructions(width, depth))
    
    # 2. Wall Logic
    plaster_thickness = 4
    
    # 2.1 Plaster (Exterior Panel)
    patch_size = 4
    for x in range(0, width, patch_size):
        for z in range(40, height, patch_size):
            # Use GLOBAL X for noise continuity
            true_x = global_x_offset + x
            
            noise_val = math.sin(true_x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_w = min(patch_size, width - x)
            p_h = min(patch_size, height - z)
            
            local_x = x - half_w
            
            instructions.append({
                "op": "add",
                "pos": [local_x, wall_back_y, z],
                "size": [p_w, plaster_thickness, p_h],
                "color": shade
            })
            
    # 2.2 Wainscoting
    # Brick pattern alignment
    # Since width (192 or 160) is multiple of brick_len (8), we can just generate locally
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    instructions.extend(csg_patterns.create_brick_volume(
        start_pos=(-half_w, wall_back_y, 0),
        size=(width, plaster_thickness, 40),
        brick_size=(8, 4, 4),
        color=stone_mix,
        mortar=1
    ))
    
    # 2.3 Beams
    beam_thick = 12
    beam_h_dim = 6
    
    for z in [0, 40, height - beam_h_dim]:
        instructions.append({
            "op": "add",
            "pos": [-half_w, wall_back_y, z],
            "size": [width, beam_thick, beam_h_dim],
            "color": palette.WOOD_DARK
        })
        
    # Output
    data = {
        "name": name,
        "asset_tags": tags,
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -half_d, 0]},
            "south": {"pos": [0, half_d, 0]},
            "east": {"pos": [half_w, 0, 0]},
            "west": {"pos": [-half_w, 0, 0]},
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), f"../../csg/{name}.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

def generate_wall_mega_plaster_A_11():
    # Part 1: 6 tiles = 192 units
    # Starts at x=16 (physically) relative to corner end
    generate_segment(
        "wall_mega_plaster_A_part1", 
        width=192, height=96, depth=32, 
        global_x_offset=16, total_width=352,
        tags=["structure", "wall", "north", "plaster", "mega_base", "part1"]
    )
    
    # Part 2: 5 tiles = 160 units
    # Starts at 16 + 192 = 208
    generate_segment(
        "wall_mega_plaster_A_part2", 
        width=160, height=96, depth=32, 
        global_x_offset=208, total_width=352,
        tags=["structure", "wall", "north", "plaster", "mega_base", "part2"]
    )

if __name__ == "__main__":
    generate_wall_mega_plaster_A_11()