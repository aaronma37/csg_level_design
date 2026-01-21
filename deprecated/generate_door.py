import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_door
import palette

def generate_door():
    print("Generating Tavern Door...")
    scene = make_door(30, 50)
    instructions = scene.get_instructions()
    data = {"name": "door", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/door.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created door with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_door()
