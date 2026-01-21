import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_bottle
import palette

def generate_bottle():
    print("Generating Glass Bottle...")
    scene = make_bottle(palette.FABRIC_BLUE) # Blue glass
    instructions = scene.get_instructions()
    data = {"name": "bottle", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/bottle.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created bottle with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_bottle()
