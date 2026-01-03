import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_window
import palette

def generate_window():
    print("Generating Detailed Window...")
    scene = make_window(24, 32)

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "window", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/window.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created window with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_window()
