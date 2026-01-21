import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
import random
import palette

def generate_floor():
    random.seed(1337)
    instructions = []
    
    # Standard Tile Size: 3.2 CU x 3.2 CU
    f_w = 160
    f_d = 160
    f_h = 2
    
    # Solid backing (Dark)
    instructions.append({
        "op": "add",
        "pos": [0, 0, 0],
        "size": [f_w, f_d, 1],
        "color": palette.WOOD_DARK
    })
    
    # Plank Pattern
    # Length 32, Width 6, Thickness 1
    planks = csg_patterns.create_plank_volume(
        start_pos=(0, 0, 1),
        size=(f_w, f_d, 1),
        plank_size=(32, 6, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y' # Long along Y
    )
    instructions.extend(planks)
    
    data = {
        "name": "wooden_floor",
        "instructions": instructions
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/wooden_floor.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_floor()
