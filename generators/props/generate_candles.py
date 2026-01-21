import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_candle
import palette

def generate_candles():
    print("Composing a cluster of candles...")
    scene = VoxelBuilder()

    # Add three candles with different heights and slight offsets
    scene.add_component(make_candle(6), ox=0, oy=0, oz=0)
    scene.add_component(make_candle(4), ox=2, oy=1, oz=0)
    scene.add_component(make_candle(5), ox=-1, oy=2, oz=0)

    # Save to JSON
    instructions = scene.get_instructions()
    data = {"name": "candles", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/candles.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created candle cluster with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_candles()
