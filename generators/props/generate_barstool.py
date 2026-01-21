import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_barstool
import palette

def generate_barstool():
    print("Generating Barstool...")
    scene = make_barstool()
    instructions = scene.get_instructions()
    data = {"name": "barstool", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/barstool.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created barstool with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_barstool()
