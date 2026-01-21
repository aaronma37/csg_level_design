import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from patterns import csg_patterns
import random
import palette

def generate_tall_wall():
    random.seed(1337)
    w = 64
    h = 160
    d = 8 # Wall thickness
    
    instructions = []
    
    # --- 1. Base Stone Foundation (Bottom 48 units) ---
    brick_w = 16
    brick_h = 6
    for row in range(8):
        z_offset = row * brick_h
        row_shift = (row % 2) * (brick_w // 2)
        for i in range(-1, 5):
            x_pos = -w//2 + (i * brick_w) + row_shift
            
            actual_x = max(-w//2, x_pos)
            actual_w = brick_w - (actual_x - x_pos)
            if actual_x + actual_w > w//2:
                actual_w = w//2 - actual_x
                
            if actual_w > 0:
                instructions.append({
                    "op": "add",
                    "pos": [actual_x, 0, z_offset],
                    "size": [actual_w, d, brick_h - 1],
                    "color": palette.STONE_BASE if (i+row)%3 != 0 else palette.STONE_DARK
                })

    # --- 2. Timber Framework (Top Section) ---
    # Main horizontal beam between Stone and Wood
    instructions.append({
        "op": "add",
        "pos": [-w//2, 0, 48],
        "size": [w, d+2, 4],
        "color": palette.WOOD_DARK
    })
    
    # Top horizontal plate
    instructions.append({
        "op": "add",
        "pos": [-w//2, 0, h-4],
        "size": [w, d+2, 4],
        "color": palette.WOOD_DARK
    })
    
    # Side Vertical Pillars (The Seam-Hiders)
    # These pillars sit at the edges to ensure tiles connect seamlessly
    instructions.append({
        "op": "add",
        "pos": [-w//2, -1, 0],
        "size": [4, d+4, h],
        "color": palette.WOOD_DARK
    })
    instructions.append({
        "op": "add",
        "pos": [w//2 - 4, -1, 0],
        "size": [4, d+4, h],
        "color": palette.WOOD_DARK
    })
    
    # Middle fill (Plaster Panels)
    instructions.append({
        "op": "add",
        "pos": [-w//2 + 4, 1, 52],
        "size": [w - 8, d - 2, h - 56],
        "color": palette.BEIGE_LIGHT
    })
    
    # Vertical studs in the middle
    for x in [-16, 16]:
        instructions.append({
            "op": "add",
            "pos": [x-2, -1, 52],
            "size": [4, d+2, h-56],
            "color": palette.WOOD_DARK
        })

    data = {
        "name": "tavern_wall_tall",
        "instructions": instructions
    }
    
    with open("csg/tavern_wall_tall.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_tall_wall()
