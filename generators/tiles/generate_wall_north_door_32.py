import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns
from patterns.micro_props import make_door
import math

def generate_wall_north_door_32():
    instructions = []
    
    # --- 1. Floor Generation (Base 32x32) ---
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
    # Bricks are 8x4x4. 
    # We'll just generate them and the door cutout will be handled by the fact we skip them.
    # Actually create_brick_volume doesn't have a cutout. 
    # Let's just use add ops for the wainscoting to respect the door.
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
    # Horizontal Beams: Full Thickness [-16, -4]
    for z in [0, 40, w_h - 6]:
        # Only draw if not interrupted by door? 
        # Z=0 is interrupted. Z=40 is interrupted. Z=90 is NOT.
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
    # make_door returns a VoxelBuilder. 
    # We want it at Y = wall_back_y + 2 (slightly recessed)
    door_b = make_door(door_w, door_h)
    door_instr = door_b.get_instructions()
    # door_b is centered on X=0, Y=0. Z starts at 0.
    # We need to offset it to center of door cutout.
    # door_x_center = door_x_start + door_w/2 - half_size = 6 + 10 - 16 = 0.
    for inst in door_instr:
        inst['pos'][1] += (wall_back_y + 4) # Recess it
        instructions.append(inst)

    # Output
    data = {
        "name": "wall_north_door_32",
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [0, 0, 0]},
            "north": {"pos": [0, -16, 0]},
            "south": {"pos": [0, 16, 0]},
            "east": {"pos": [16, 0, 0]},
            "west": {"pos": [-16, 0, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/wall_north_door_32.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    import random
    random.seed(42)
    generate_wall_north_door_32()
