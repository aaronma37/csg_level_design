import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
from generators.floors import floor_wood_plain
import random
import palette

def generate_floor_bevel_size(size, variants=1):
    # Dimensions
    f_w = size
    f_d = size
    
    for i in range(variants):
        # Seed ensures reproducibility per variant (though generic floor is uniform now)
        random.seed(1337 + i)
        
        # Use shared generator
        instructions = floor_wood_plain.get_instructions(f_w, f_d)
        
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
        
        output_path = os.path.join(os.path.dirname(__file__), f"../../csg/{name}.json")
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_floor_bevel_size(32, variants=3) # Generate A, B, C
