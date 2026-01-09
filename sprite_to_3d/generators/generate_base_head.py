import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import json
from tools.builder import VoxelBuilder
import palette

def generate():
    print("Generating Base Head...")
    scene = VoxelBuilder()
    
    # 3 voxel long line along x axis
    # Using color 100 (Character Range start)
    scene.line(0, 0, 0, 2, 0, 0, 100) 

    instructions = scene.get_instructions()
    data = {"name": "base_head", "instructions": instructions}
    # Outputting to csg directory
    output_path = os.path.join(os.path.dirname(__file__), "../../csg/base_head.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! Created Base Head with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate()
