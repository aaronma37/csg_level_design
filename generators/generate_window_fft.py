import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette

def generate_window():
    w, h, d = 40, 60, 4
    instr = []
    # Frame
    instr.append({"op": "add", "pos": [-w//2, 0, 0], "size": [w, d, h], "color": palette.WOOD_DARK})
    # Glass (Cutter)
    instr.append({"op": "subtract", "pos": [-w//2+4, -1, 4], "size": [w-8, d+2, h-8]})
    # Glass (Visible)
    instr.append({"op": "add", "pos": [-w//2+4, d//2, 4], "size": [w-8, 1, h-8], "color": palette.WINDOW_GLOW})
    
    with open("csg/window_64.json", "w") as f:
        json.dump({"name": "window_64", "instructions": instr}, f, indent=2)

if __name__ == "__main__":
    generate_window()
