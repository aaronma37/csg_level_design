import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
import random
import palette

def generate_floor_bevel_64():
    random.seed(1337)
    instructions = []
    
    # Standard Tile Size: 64x64 voxels
    f_w = 64
    f_d = 64
    
    # 1. Base Layer (Dark wood acting as the "grout" or bevel)
    # Centered at (0,0,0) in logical space, but CSG uses corner-based or center-based depending on impl.
    # Looking at floor_64.json, it uses 'add' with 'pos'.
    # If I use create_plank_volume it might expect something specific.
    # Let's stick to raw instructions for clarity or use the helper carefully.
    
    # Using centered coordinates (-32 to 32) as per floor_64.json conventions.
    
    # Base: Full 64x64 at Z=0
    instructions.append({
        "op": "add",
        "pos": [-32, -32, 0],
        "size": [64, 64, 1],
        "color": palette.WOOD_DARK
    })
    
    # 2. Surface Layer (Planks)
    # Inset by 1 voxel on all sides:
    # X: -31 to 31 (width 62)
    # Y: -31 to 31 (depth 62)
    # Z: 1 (height 1)
    
    # We can use csg_patterns if we want nice variation, or simple blocks.
    # Let's use csg_patterns for the "plank" look.
    # create_plank_volume args: start_pos, size, plank_size, color, mortar, direction
    
    # We want the planks to fill the 62x62 area starting at (-31, -31, 1).
    # Plank size: Let's say 8 wide, various lengths?
    # standard floor_64.json has planks around 5 wide.
    
    planks = csg_patterns.create_plank_volume(
        start_pos=(-31, -31, 1),
        size=(62, 62, 1),
        plank_size=(16, 5, 1), # 16 long, 5 wide
        color=[palette.WOOD_BROWN, palette.WOOD_LIGHT],
        mortar=1, # 1 voxel gap between planks inside the tile too?
                  # If mortar=1, we see the stuff below? 
                  # csg_patterns usually adds "mortar" as gaps. 
                  # If we want the bevel only on the outside, we should set mortar=0 or fill the gaps.
                  # But internal gaps (grooves) are good for texture.
        direction='y'
    )
    
    # The pattern generator might put gaps that reveal "nothing" (air) if we don't have a base.
    # We have a base at Z=0, so gaps at Z=1 will show the base color (WOOD_DARK). Perfect.
    
    instructions.extend(planks)
    
    data = {
        "name": "floor_bevel_64",
        "instructions": instructions
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/floor_bevel_64.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_floor_bevel_64()
