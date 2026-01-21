import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import palette

def get_instructions(width, depth):
    instructions = []
    
    # 1. Base Layer (Dark Grout/Bevel)
    instructions.append({
        "op": "add",
        "pos": [-width//2, -depth//2, 0],
        "size": [width, depth, 1],
        "color": palette.WOOD_DARK
    })
    
    # 2. Surface Layer (Solid Wood)
    # Inset by 1 unit to reveal the bevel
    instructions.append({
        "op": "add",
        "pos": [-width//2 + 1, -depth//2 + 1, 1],
        "size": [width - 2, depth - 2, 1],
        "color": palette.WOOD_BROWN
    })
    
    return instructions
