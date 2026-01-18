import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
import palette

def generate_modular_bar():
    tile_size = 64
    hw = tile_size // 2
    
    # --- 1. Bar Straight (64 wide, 14 deep) ---
    b_s = VoxelBuilder()
    # Base
    b_s.fill(-hw, 0, 0, hw, 6, 35, palette.WOOD_DARK)
    # Rail
    b_s.fill(-hw, 1, 1, hw, 2, 2, palette.STONE_DARK)
    # Counter
    b_s.fill(-hw, 0, 35, hw, 14, 38, palette.WOOD_BROWN)
    # Corbels
    for x in [-hw+8, 0, hw-8]:
        b_s.fill(x-1, 6, 25, x+1, 10, 35, palette.WOOD_DARK)
    
    with open("csg/bar_straight_64.json", "w") as f:
        json.dump({"name": "bar_straight_64", "instructions": b_s.get_instructions()}, f, indent=2)

    # --- 2. Bar Corner (Connecting North and West edges) ---
    b_c = VoxelBuilder()
    # North segment (along +Y edge)
    b_c.fill(-hw, hw-14, 0, hw, hw-8, 35, palette.WOOD_DARK) # Base
    b_c.fill(-hw, hw-14, 35, hw, hw, 38, palette.WOOD_BROWN) # Counter
    
    # West segment (along -X edge)
    b_c.fill(-hw, -hw, 0, -hw+6, hw, 35, palette.WOOD_DARK) # Base
    b_c.fill(-hw, -hw, 35, 0, hw, 38, palette.WOOD_BROWN) # Counter
    
    # Clean up the interior corner overlap
    b_c.fill(-hw, hw-14, 0, -hw+14, hw, 38, palette.WOOD_BROWN) # Corner cap
    
    with open("csg/bar_corner_64.json", "w") as f:
        json.dump({"name": "bar_corner_64", "instructions": b_c.get_instructions()}, f, indent=2)

if __name__ == "__main__":
    generate_modular_bar()
