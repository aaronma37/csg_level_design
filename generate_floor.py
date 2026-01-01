import json
import csg_patterns
import random
import palette

def generate_floor():
    random.seed(1337)
    instructions = []
    
    # Dimensions
    f_w = 164
    f_d = 256
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
    
    with open("wooden_floor.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_floor()
