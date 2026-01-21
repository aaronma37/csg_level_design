import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
import palette

def generate_lantern():
    b = VoxelBuilder()
    
    # 1. Bracket Arm (Extending from 0 to -16, so it points towards camera)
    b.fill(-1, -16, 0, 1, 0, 2, palette.WOOD_DARK)
    b.fill(-3, -2, -4, 3, 0, 4, palette.WOOD_DARK) # Wall plate
    
    # 2. Lantern Housing frame (at the end of the arm: y=-16)
    # Top/Bottom caps
    b.fill(-5, -22, 6, 5, -10, 8, palette.WOOD_DARK)
    b.fill(-5, -22, -10, 5, -10, -8, palette.WOOD_DARK)
    
    # Corner struts (4 thin pillars)
    for x, y in [(-5, -22), (4, -22), (-5, -11), (4, -11)]:
        b.fill(x, y, -8, x+1, y+1, 6, palette.WOOD_DARK)
    
    # 3. The Glow Core (Fire Core)
    # Centered in housing
    b.fill(-2, -19, -5, 2, -13, 3, palette.FIRE_CORE)
    
    with open("csg/wall_lantern_64.json", "w") as f:
        json.dump({"name": "wall_lantern_64", "instructions": b.get_instructions()}, f, indent=2)

if __name__ == "__main__":
    generate_lantern()
