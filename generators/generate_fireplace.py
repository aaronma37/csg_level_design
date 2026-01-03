import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
from tools import units
import random
import palette

def generate_fireplace():
    random.seed(42)
    instructions = []
    
    # Dimensions
    fp_w = units.to_voxels(1.0) # Width of a character
    fp_d = units.to_voxels(0.5) 
    fp_total_h = units.to_voxels(2.8) # Tall floor-to-ceiling stack
    
    fp_x = 0
    fp_y = 0
    fp_z = 0
    
    # Sections
    h_base = units.to_voxels(0.65) # Above waist
    h_taper = units.to_voxels(0.4)
    h_stack = fp_total_h - h_base - h_taper 
    
    z_base = fp_z
    z_taper = z_base + h_base
    z_stack = z_taper + h_taper
    
    w_base = fp_w
    w_stack = 30
    d_base = fp_d
    d_stack = 15
    
    # Taper Alignment: Center X (0.5), Back Y (1.0)
    align_x = 0.5
    align_y = 1.0 
    
    # --- 0. SOLID BACKING (Core) ---
    print("Adding solid backing...")
    instructions.append({
        "op": "add",
        "pos": [fp_x + 2, fp_y + 2, z_base],
        "size": [w_base - 4, d_base - 4, h_base],
        "color": palette.STONE_DARKER
    })
    
    step_h = 2
    for z in range(0, h_taper, step_h):
        progress = z / float(h_taper)
        cur_w = int(w_base + (w_stack - w_base) * progress)
        cur_d = int(d_base + (d_stack - d_base) * progress)
        off_x = int((w_base - cur_w) * align_x)
        off_y = int((d_base - cur_d) * align_y)
        instructions.append({
            "op": "add",
            "pos": [fp_x + off_x + 2, fp_y + off_y + 2, z_taper + z],
            "size": [cur_w - 4, cur_d - 4, step_h],
            "color": palette.STONE_DARKER
        })
        
    off_x_stack = int((w_base - w_stack) * align_x)
    off_y_stack = int((d_base - d_stack) * align_y)
    instructions.append({
        "op": "add",
        "pos": [fp_x + off_x_stack + 2, fp_y + off_y_stack + 2, z_stack],
        "size": [w_stack - 4, d_stack - 4, h_stack],
        "color": palette.STONE_DARKER
    })

    # --- 1. BRICK STRUCTURE ---
    print("Generating brick structure...")
    stone_mix = [palette.STONE_LIGHT, palette.STONE_LIGHT, palette.STONE_DARK]
    
    # A. Base Section
    base_bricks = csg_patterns.create_brick_volume(
        start_pos=(fp_x, fp_y, z_base),
        size=(w_base, d_base, h_base),
        brick_size=(6, 5, 4),
        color=stone_mix,
        mortar=1,
        randomize_layout=True,
        mortar_noise=1
    )
    instructions.extend(base_bricks)
    
    # B. Taper Section
    taper_bricks = csg_patterns.create_brick_volume(
        start_pos=(fp_x, fp_y, z_taper),
        size=(w_base, d_base, h_taper),
        end_size=(w_stack, d_stack), 
        brick_size=(5, 5, 4),
        color=stone_mix,
        mortar=1,
        randomize_layout=True,
        taper_align=(align_x, align_y),
        mortar_noise=1
    )
    instructions.extend(taper_bricks)
    
    # C. Stack Section (Stop 4 voxels early for the crown)
    h_stack_bricks = h_stack - 4
    stack_bricks = csg_patterns.create_brick_volume(
        start_pos=(fp_x + off_x_stack, fp_y + off_y_stack, z_stack),
        size=(w_stack, d_stack, h_stack_bricks),
        brick_size=(6, 5, 4),
        color=stone_mix,
        mortar=1,
        randomize_layout=True,
        mortar_noise=1
    )
    instructions.extend(stack_bricks)

    # --- 1.5 CHIMNEY CROWN/POT ---
    print("Adding chimney crown...")
    crown_h = 4
    z_crown = fp_total_h - crown_h
    
    # Wider Crown Slab
    instructions.append({
        "op": "add",
        "pos": [fp_x + off_x_stack - 1, fp_y + off_y_stack - 1, z_crown],
        "size": [w_stack + 2, d_stack + 2, 2],
        "color": palette.STONE_DARK
    })
    
    # Chimney Pot (Centered on top)
    pot_w, pot_d = 14, 10
    pot_x = fp_x + off_x_stack + (w_stack - pot_w) // 2
    pot_y = fp_y + off_y_stack + (d_stack - pot_d) // 2
    
    instructions.append({
        "op": "add",
        "pos": [pot_x, pot_y, z_crown + 2],
        "size": [pot_w, pot_d, 2],
        "color": palette.STONE_DARKER
    })
    
    # --- 2. CARVING ---
    fire_w = units.to_voxels(0.6)
    fire_h = units.to_voxels(0.45)
    fire_d = units.to_voxels(0.35)
    fire_x = fp_x + (fp_w - fire_w) // 2
    fire_z = fp_z + 2
    print("Carving firebox...")
    instructions.append({
        "op": "subtract",
        "pos": [fire_x, fp_y, fire_z],
        "size": [fire_w, fire_d, fire_h]
    })
    
    flue_w = units.to_voxels(0.24)
    flue_d = units.to_voxels(0.16) 
    flue_h = fp_total_h - (fire_z + fire_h)
    stack_center_x = fp_x + off_x_stack + (w_stack // 2)
    stack_center_y = fp_y + off_y_stack + (d_stack // 2)
    flue_x = stack_center_x - (flue_w // 2)
    flue_y = stack_center_y - (flue_d // 2)
    flue_z = fire_z + fire_h
    print("Carving flue...")
    instructions.append({
        "op": "subtract",
        "pos": [flue_x, flue_y, flue_z],
        "size": [flue_w, flue_d, flue_h]
    })
    
    # --- 3. DETAILS ---
    mantel_h = 4
    mantel_d = units.to_voxels(0.24)
    mantel_z = fire_z + fire_h + 2 
    print("Adding mantel...")
    instructions.append({
        "op": "add",
        "pos": [fp_x - 2, fp_y - 2, mantel_z],
        "size": [fp_w + 4, mantel_d, mantel_h],
        "color": palette.WOOD_DARK
    })
    
    print("Adding fire...")
    instructions.append({
        "op": "add",
        "pos": [fire_x + 8, fp_y + 4, fire_z],
        "size": [fire_w - 16, 4, 4],
        "color": palette.WOOD_DARK
    })
    instructions.append({
        "op": "add",
        "pos": [fire_x + 10, fp_y + 6, fire_z + 2],
        "size": [fire_w - 20, 4, 8],
        "color": palette.RED
    })
    instructions.append({
        "op": "add",
        "pos": [fire_x + 12, fp_y + 7, fire_z + 3],
        "size": [fire_w - 24, 2, 6],
        "color": palette.FIRE_ORANGE
    })

    data = {
        "name": "stone_fireplace",
        "instructions": instructions
    }
    with open("../csg/stone_fireplace.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_fireplace()
