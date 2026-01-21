import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import palette
from generators.floors import floor_wood_plain
from patterns import csg_patterns
from patterns.micro_props import make_door
import math

def generate_wall_north_door_32():
    instructions = []
    
    # --- 1. Floor Generation (Base 32x32) ---
    instructions.extend(floor_wood_plain.get_instructions(32, 32))

    # --- 2. Wall Generation (North Edge) ---
    f_size = 32
    half_size = f_size // 2 # 16
    w_len = 32
    w_h = 96
    wall_back_y = -16
    wall_front_y = -4
    beam_thick = 12
    plaster_thick = 4
    
    # Door Cutout dimensions
    door_w = 20
    door_h = 60
    door_x_start = (w_len - door_w) // 2 # 6
    door_x_end = door_x_start + door_w # 26
    
    # 2.1 Plaster (Exterior Panel) - with door cutout
    patch_size = 4
    for x in range(0, w_len, patch_size):
        for z in range(40, w_h, patch_size):
            # Skip if inside door cutout
            if x >= door_x_start and x < door_x_end and z < door_h:
                continue
                
            noise_val = math.sin(x * 0.05) + math.cos(z * 0.05)
            shade = palette.BEIGE_MEDIUM if noise_val < 0.3 else palette.BEIGE_LIGHT
            
            p_w = min(patch_size, w_len - x)
            p_h = min(patch_size, w_h - z)
            
            instructions.append({
                "op": "add",
                "pos": [x - half_size, wall_back_y, z],
                "size": [p_w, plaster_thick, p_h],
                "color": shade
            })
            
    # 2.2 Stone Wainscoting - with door cutout
    stone_mix = [palette.STONE_LIGHT, palette.STONE_DARK]
    for x in range(0, w_len, 8):
        for z in range(0, 40, 4):
            if x >= door_x_start and x < door_x_end and z < door_h:
                continue
            color = random.choice(stone_mix)
            instructions.append({
                "op": "add",
                "pos": [x - half_size, wall_back_y, z],
                "size": [8, plaster_thick, 4],
                "color": color
            })

    # 2.3 Beams (Frame)
    for z in [0, 40, w_h - 6]:
        if z < door_h:
            # Left part
            if door_x_start > 0:
                instructions.append({
                    "op": "add",
                    "pos": [-half_size, wall_back_y, z],
                    "size": [door_x_start, beam_thick, 6],
                    "color": palette.WOOD_DARK
                })
            # Right part
            if door_x_end < w_len:
                instructions.append({
                    "op": "add",
                    "pos": [door_x_end - half_size, wall_back_y, z],
                    "size": [w_len - door_x_end, beam_thick, 6],
                    "color": palette.WOOD_DARK
                })
        else:
            instructions.append({
                "op": "add",
                "pos": [-half_size, wall_back_y, z],
                "size": [w_len, beam_thick, 6],
                "color": palette.WOOD_DARK
            })
            
    # Vertical Beams: Full Thickness [-16, -4]
    for x_rel in [0, door_x_start, door_x_end - 4, w_len - 6]:
        instructions.append({
            "op": "add",
            "pos": [x_rel - half_size, wall_back_y, 0],
            "size": [4 if x_rel in [door_x_start, door_x_end-4] else 6, beam_thick, w_h if x_rel in [0, w_len-6] else door_h],
            "color": palette.WOOD_DARK
        })

    # --- 3. The Door ---
    door_b = make_door(door_w, door_h)
    door_instr = door_b.get_instructions()
    for inst in door_instr:
        inst['pos'][1] += (wall_back_y + 4) # Recess it
        instructions.append(inst)

    # Output
    data = {
        "name": "wall_north_door_32",
        "asset_tags": ["structure", "wall", "doorway", "north", "base"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "south": {"pos": [0, 16, 0]},
            "east": {"pos": [16, 0, 0]},
            "west": {"pos": [-16, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/wall_north_door_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    import random
    random.seed(42)
    generate_wall_north_door_32()
