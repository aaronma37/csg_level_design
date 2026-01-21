import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
import random
import palette

def generate_floor_bevel_size(size, variants=1):
    # Dimensions
    f_w = size
    f_d = size
    half_size = size // 2
    
    # Adjust plank dimensions slightly for smaller tiles
    p_len = 16
    p_wid = 5
    mortar_val = 1
    
    for i in range(variants):
        # Seed ensures reproducibility per variant
        random.seed(1337 + i)
        
        instructions = []
        
        # 1. Base Layer (Dark wood acting as the "grout" or bevel)
        instructions.append({
            "op": "add",
            "pos": [-half_size, -half_size, 0],
            "size": [f_w, f_d, 1],
            "color": palette.WOOD_DARK
        })
        
        # 2. Surface Layer (Planks)
        plank_area_size = size - 2
        start_pos = (-half_size + 1, -half_size + 1, 1)
        
        planks = csg_patterns.create_plank_volume(
            start_pos=start_pos,
            size=(plank_area_size, plank_area_size, 1),
            plank_size=(p_len, p_wid, 1),
            color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
            mortar=mortar_val,
            direction='y',
            paint_mortar=True,
            mortar_color=palette.WOOD_DARK
        )
        
        instructions.extend(planks)
        
        suffix = f"_var{i+1}" if variants > 1 else ""
        name = f"floor_bevel_{size}{suffix}"
        
        data = {
            "name": name,
            "instructions": instructions,
            "snap_points": {
                "north": {"pos": [0, -16, 0]},
                "south": {"pos": [0, 16, 0]},
                "east": {"pos": [16, 0, 0]},
                "west": {"pos": [-16, 0, 0]},
                "north_outer": {"pos": [0, -20, 0]},
                "south_outer": {"pos": [0, 20, 0]},
                "east_outer": {"pos": [20, 0, 0]},
                "west_outer": {"pos": [-20, 0, 0]},
                "center": {"pos": [0, 0, 0]}
            }
        }
        
        output_path = os.path.join(os.path.dirname(__file__), f"../csg/{name}.json")
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_floor_bevel_size(32, variants=3) # Generate A, B, C
