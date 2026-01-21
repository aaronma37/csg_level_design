import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_bar_counter
import palette

def generate_bar():
    print("Generating Bar Counter...")
    scene = make_bar_counter(64)
    instructions = scene.get_instructions()
    data = {"name": "bar_counter", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/bar_counter.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created bar counter with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_bar()
