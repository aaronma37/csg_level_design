import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns.micro_props import make_railing
import palette

def generate_railings():
    print("Generating Railing Variants...")
    
    # 1. Long Railing (160 units)
    scene_long = make_railing(160)
    data_long = {"name": "railing_long", "instructions": scene_long.get_instructions()}
    out_long = os.path.join(os.path.dirname(__file__), "../csg/railing_long.json")
    with open(out_long, "w") as f: json.dump(data_long, f, indent=2)
    
    # 2. Short Railing (80 units)
    scene_short = make_railing(80)
    data_short = {"name": "railing_short", "instructions": scene_short.get_instructions()}
    out_short = os.path.join(os.path.dirname(__file__), "../csg/railing_short.json")
    with open(out_short, "w") as f: json.dump(data_short, f, indent=2)
    
    print(f"Done! Created long and short railing variants.")

if __name__ == "__main__":
    generate_railings()
