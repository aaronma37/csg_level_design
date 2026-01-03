import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_skull, make_plaque
import palette

def generate_trophy_wall():
    print("Composing Trophy Wall Asset...")
    scene = VoxelBuilder()

    # 1. Add the Plaque (The base)
    plaque = make_plaque(14, 18)
    scene.add_component(plaque, ox=0, oy=0, oz=0)

    # 2. Add the Skull (Mounted on the plaque)
    # The skull is centered at 0,0,0 and about 10v tall.
    # We'll shift it forward (Y+) and slightly up (Z+)
    skull = make_skull()
    scene.add_component(skull, ox=0, oy=1, oz=2)

    # 3. Add a little "nameplate" (Golden trim)
    scene.fill(-3, 2, -6, 3, 2, -5, palette.FIRE_CORE) # Using fire as gold

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "trophy_wall", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/trophy_wall.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created composite trophy wall with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_trophy_wall()
