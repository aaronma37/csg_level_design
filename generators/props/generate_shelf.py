import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_shelf
import palette

def generate_shelf():
    print("Generating Bar Shelf...")
    scene = make_shelf(64, 3)
    instructions = scene.get_instructions()
    data = {"name": "shelf", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/shelf.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created shelf with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_shelf()
