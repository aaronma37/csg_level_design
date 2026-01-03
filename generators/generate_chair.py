import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_sturdy_chair
import palette

def generate_chair():
    print("Generating Properly Scaled Sturdy Chair...")
    scene = make_sturdy_chair()

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "chair", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/chair.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created scaled chair with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_chair()
