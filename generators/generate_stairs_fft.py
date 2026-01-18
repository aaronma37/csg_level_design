import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
from patterns import csg_patterns
import palette

def generate_stairs():
    tile_size = 64
    hw = tile_size // 2
    b = VoxelBuilder()
    
    # 4 Steps, each 16 units deep, 4 units high
    for i in range(4):
        z_base = i * 4
        y_start = -hw + (i * 16)
        
        # 1. Solid Step Base
        b.fill(-hw, y_start, 0, hw, y_start + 16, z_base + 3, palette.WOOD_DARK)
        
        # 2. Plank Pattern on step top
        # We'll use the same colors as floor_64
        for x in range(-hw, hw, 8): # Plank width 8
            for y in range(y_start, y_start + 16, 16): # Plank length 16
                color = palette.WOOD_BROWN if (x//8 + i)%2 == 0 else palette.WOOD_LIGHT
                b.fill(x, y, z_base + 3, x + 7, y + 15, z_base + 4, color)

    # 3. Handrails (Left and Right edges)
    for x in [-hw, hw-4]:
        for i in range(4):
            z_base = i * 4
            y_start = -hw + (i * 16)
            # Post
            b.fill(x, y_start, z_base + 4, x + 4, y_start + 4, z_base + 12, palette.WOOD_DARK)
            # Rail segment (following the slope)
            b.fill(x, y_start, z_base + 12, x + 4, y_start + 16, z_base + 16, palette.WOOD_DARK)

    with open("csg/stairs_64.json", "w") as f:
        json.dump({"name": "stairs_64", "instructions": b.get_instructions()}, f, indent=2)

if __name__ == "__main__":
    generate_stairs()
