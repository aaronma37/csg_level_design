import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
import random
import palette

def generate_tile_assets():
    random.seed(42)
    tile_size = 64
    
    # --- 1. Wooden Floor (80x80) ---
    floor_instr = []
    floor_instr.append({
        "op": "add",
        "pos": [-tile_size//2, -tile_size//2, 0],
        "size": [tile_size, tile_size, 1],
        "color": palette.WOOD_DARK
    })
    planks = csg_patterns.create_plank_volume(
        start_pos=(-tile_size//2, -tile_size//2, 1),
        size=(tile_size, tile_size, 1),
        plank_size=(20, 5, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y'
    )
    floor_instr.extend(planks)
    
    with open("csg/floor_64.json", "w") as f:
        json.dump({"name": "floor_64", "instructions": floor_instr}, f, indent=2)

    # --- 2. Wooden Block (80x80x16) for elevation ---
    block_instr = []
    # Solid sides
    block_instr.append({
        "op": "add",
        "pos": [-tile_size//2, -tile_size//2, 0],
        "size": [tile_size, tile_size, 16],
        "color": palette.WOOD_DARK
    })
    # Top surface (planks)
    planks_top = csg_patterns.create_plank_volume(
        start_pos=(-tile_size//2, -tile_size//2, 16),
        size=(tile_size, tile_size, 1),
        plank_size=(20, 5, 1),
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1,
        direction='y'
    )
    block_instr.extend(planks_top)
    
    with open("csg/block_64.json", "w") as f:
        json.dump({"name": "block_64", "instructions": block_instr}, f, indent=2)

if __name__ == "__main__":
    generate_tile_assets()
