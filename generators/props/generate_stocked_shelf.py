import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random
import palette

def generate_stocked_shelf():
    w, h, d = 48, 80, 12
    instr = []
    # 1. Outer Frame
    instr.append({"op": "add", "pos": [-w//2, 0, 0], "size": [w, d, h], "color": palette.WOOD_DARK})
    instr.append({"op": "subtract", "pos": [-w//2+2, -1, 4], "size": [w-4, d+2, h-8]})
    
    # 2. Horizontal Shelves (at z=25, 50)
    for z in [25, 50]:
        instr.append({"op": "add", "pos": [-w//2+2, 0, z], "size": [w-4, d, 2], "color": palette.WOOD_DARK})
        
        # 3. Add random "Books" on each shelf
        random.seed(z)
        x_cursor = -w//2 + 4
        while x_cursor < w//2 - 8:
            bw = random.randint(2, 4)
            bh = random.randint(12, 18)
            bd = random.randint(6, 10)
            color = random.choice([palette.FABRIC_RED, palette.FABRIC_BLUE, palette.FABRIC_MAROON, palette.STONE_BASE])
            instr.append({"op": "add", "pos": [x_cursor, 1, z+2], "size": [bw, bd, bh], "color": color})
            x_cursor += bw + 1

    with open("csg/stocked_shelf_64.json", "w") as f:
        json.dump({"name": "stocked_shelf_64", "instructions": instr}, f, indent=2)

if __name__ == "__main__":
    generate_stocked_shelf()
