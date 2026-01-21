import sys
import os

# Add project root to path so we can import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from tools import project
from tools.schema import Asset
from tools.builder import VoxelBuilder
from patterns.micro_props import make_candle

def generate_candles():
    print("Composing a cluster of candles...")
    scene = VoxelBuilder()

    # Add three candles with different heights and slight offsets
    scene.add_component(make_candle(6), ox=0, oy=0, oz=0)
    scene.add_component(make_candle(4), ox=2, oy=1, oz=0)
    scene.add_component(make_candle(5), ox=-1, oy=2, oz=0)

    # Define Asset using Strict Schema
    asset = Asset(
        name="candles",
        asset_tags=["decor", "light_source", "clutter"],
        instructions=scene.get_instructions()
    )
    
    # Add Light Emitter (Type Safe)
    asset.add_light(
        offset=(0, 0, 5),
        color=(1.0, 0.9, 0.6),
        intensity=40
    )

    # Save using Central Path
    asset.save(project.get_asset_path("candles"))
    
    print(f"Done! Created candle cluster with {len(scene.voxels)} voxels.")

if __name__ == "__main__":
    generate_candles()
