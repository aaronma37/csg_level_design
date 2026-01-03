import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_mug
import palette

def generate_mug():
    print("Generating Wooden Mug...")
    scene = make_mug()
    instructions = scene.get_instructions()
    data = {"name": "mug", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/mug.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created mug with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_mug()
