import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette

def generate_window_wall():
    w, h, d = 64, 160, 8
    # Start with the standard tall wall instructions
    with open("csg/tavern_wall_tall.json", "r") as f:
        data = json.load(f)
    
    # Add a window cutout (centered at z=90)
    data["instructions"].append({
        "op": "subtract",
        "pos": [-20, -1, 70],
        "size": [40, d+2, 60]
    })
    
    data["name"] = "tavern_wall_window"
    with open("csg/tavern_wall_window.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_window_wall()
