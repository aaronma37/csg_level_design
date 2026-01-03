import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_tankard
import palette

def generate_tankard():
    print("Generating Iron Tankard...")
    scene = make_tankard()
    instructions = scene.get_instructions()
    data = {"name": "tankard", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/tankard.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created tankard with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_tankard()
