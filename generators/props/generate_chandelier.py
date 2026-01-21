import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import math
from tools.builder import VoxelBuilder
from patterns.micro_props import make_chain_link, make_hoop, make_candle
import palette

def generate_chandelier():
    print("Assembling Large Wooden Chandelier...")
    scene = VoxelBuilder()

    # 1. Create the hanging chain (5 links)
    link = make_chain_link()
    for i in range(5):
        current_link = VoxelBuilder()
        current_link.add_component(link)
        if i % 2 == 1:
            current_link.rotate_z(1)
        scene.add_component(current_link, ox=0, oy=0, oz=20 + (i * 3))

    # 2. Add the Large Wooden Hoop
    # Increased radius to 10, material set to Wood Dark
    radius = 10
    hoop = make_hoop(radius, palette.WOOD_DARK)
    scene.add_component(hoop, ox=0, oy=0, oz=10)

    # 3. Add Support Bars and Candles with 5-point symmetry
    # 360 / 5 = 72 degrees
    candle = make_candle(5)
    for i in range(5):
        angle = i * 72
        rad = math.radians(angle)
        x = int(round(math.cos(rad) * radius))
        y = int(round(math.sin(rad) * radius))
        
        # Support Bar (from chain bottom to hoop)
        scene.line(0, 0, 20, x, y, 10, palette.STONE_DARK)
        
        # Candle on the hoop
        scene.add_component(candle, ox=x, oy=y, oz=11)

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "chandelier", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/chandelier.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created composite chandelier with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_chandelier()