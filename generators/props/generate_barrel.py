import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_barrel
import palette

def generate_barrel():
    print("Generating Detailed Wooden Barrel...")
    scene = make_barrel(8, 22)

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "barrel", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/barrel.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created barrel with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_barrel()
