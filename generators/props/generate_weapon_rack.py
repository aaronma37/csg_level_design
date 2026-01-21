import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_weapon_rack_frame, make_shortsword, make_battleaxe, make_spear
import palette

def generate_weapon_rack():
    print("Assembling Doubled Modular Weapon Rack...")
    scene = VoxelBuilder()

    # 1. Add the Doubled Frame
    frame = make_weapon_rack_frame(32, 28)
    scene.add_component(frame)

    # 2. Add Doubled Weapons (Adjusted offsets for larger scale)
    # Spear on the left
    scene.add_component(make_spear(), ox=-8, oy=2, oz=2)
    
    # Axe in the middle
    scene.add_component(make_battleaxe(), ox=0, oy=2, oz=2)
    
    # Sword on the right
    scene.add_component(make_shortsword(), ox=8, oy=2, oz=2)

    # 3. Add Doubled "Iron" nails (micro-detail)
    for x in [-8, 0, 8]:
        scene.fill(x, 0, 6, x+1, 0, 7, palette.STONE_DARK)
        scene.fill(x, 0, 20, x+1, 0, 21, palette.STONE_DARK)

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "weapon_rack", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/weapon_rack.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created composite doubled weapon rack with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_weapon_rack()