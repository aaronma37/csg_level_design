import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_stairs
import palette

def generate_stairs():
    print("Generating Wooden Stairs...")
    scene = make_stairs(40, 80, 20)
    instructions = scene.get_instructions()
    data = {"name": "stairs", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/stairs.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created stairs with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_stairs()
