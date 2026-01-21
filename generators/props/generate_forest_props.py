import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette

def generate_props():
    print("Generating Forest Props...")

    # --- SIGNPOST ---
    sign_instr = []
    # Pole
    sign_instr.append({"op": "add", "shape": "cuboid", "pos": [0, 0, 0], "size": [4, 4, 25], "color": palette.WOOD_DARK})
    # Board
    sign_instr.append({"op": "add", "shape": "cuboid", "pos": [0, -1, 20], "size": [16, 2, 6], "color": palette.WOOD_LIGHT})
    # Text (Simulation)
    sign_instr.append({"op": "add", "shape": "cuboid", "pos": [-4, -2, 21], "size": [8, 1, 1], "color": palette.WOOD_DARK})
    
    with open(os.path.join(os.path.dirname(__file__), "../csg/forest_signpost.json"), "w") as f:
        json.dump({"name": "forest_signpost", "instructions": sign_instr}, f)

    # --- LAMP POST ---
    lamp_instr = []
    # Base
    lamp_instr.append({"op": "add", "shape": "cuboid", "pos": [-2, -2, 0], "size": [4, 4, 35], "color": palette.WOOD_DARK})
    # Hanger arm
    lamp_instr.append({"op": "add", "shape": "cuboid", "pos": [0, -2, 32], "size": [10, 2, 2], "color": palette.WOOD_DARK})
    # Lantern
    lamp_instr.append({"op": "add", "shape": "cuboid", "pos": [8, -2, 26], "size": [4, 4, 6], "color": palette.STONE_DARK}) # Iron casing
    lamp_instr.append({"op": "add", "shape": "cuboid", "pos": [9, -1, 27], "size": [2, 2, 4], "color": palette.FIRE_GLOW}) # Light
    
    with open(os.path.join(os.path.dirname(__file__), "../csg/forest_lamppost.json"), "w") as f:
        json.dump({"name": "forest_lamppost", "instructions": lamp_instr}, f)

    # --- WOODEN FENCE (Segment) ---
    fence_instr = []
    # Post L
    fence_instr.append({"op": "add", "shape": "cuboid", "pos": [0, 0, 0], "size": [4, 4, 16], "color": palette.WOOD_BROWN})
    # Post R (at 32 units)
    fence_instr.append({"op": "add", "shape": "cuboid", "pos": [28, 0, 0], "size": [4, 4, 16], "color": palette.WOOD_BROWN})
    # Rails
    fence_instr.append({"op": "add", "shape": "cuboid", "pos": [2, 1, 10], "size": [28, 2, 2], "color": palette.WOOD_LIGHT})
    fence_instr.append({"op": "add", "shape": "cuboid", "pos": [2, 1, 5], "size": [28, 2, 2], "color": palette.WOOD_LIGHT})
    
    with open(os.path.join(os.path.dirname(__file__), "../csg/forest_fence.json"), "w") as f:
        json.dump({"name": "forest_fence", "instructions": fence_instr}, f)
        
    print("Props generated.")

if __name__ == "__main__":
    generate_props()
