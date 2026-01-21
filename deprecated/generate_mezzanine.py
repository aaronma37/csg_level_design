import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_stair_railing, make_walkway_tile
import palette

def generate_mezzanine_assets():
    print("Generating Mezzanine Assets...")
    
    # 1. Stair Railing (matches stairs: 160 depth, 80 height)
    scene_sr = make_stair_railing(160, 80, 15)
    data_sr = {"name": "stair_railing", "instructions": scene_sr.get_instructions()}
    out_sr = os.path.join(os.path.dirname(__file__), "../csg/stair_railing.json")
    with open(out_sr, "w") as f: json.dump(data_sr, f, indent=2)
    
    # 2. Walkway Tile (160x32)
    scene_wt = make_walkway_tile(160, 32)
    data_wt = {"name": "walkway_tile", "instructions": scene_wt.get_instructions()}
    out_wt = os.path.join(os.path.dirname(__file__), "../csg/walkway_tile.json")
    with open(out_wt, "w") as f: json.dump(data_wt, f, indent=2)
    
    print(f"Done!")

if __name__ == "__main__":
    generate_mezzanine_assets()
