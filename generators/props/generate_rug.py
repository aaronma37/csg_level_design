import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random
from tools.builder import VoxelBuilder
import palette

def add_detailed_tassel(b, x, y, dx, dy):
    """Adds a detailed tassel at a corner. dx/dy are directions (+1 or -1)."""
    # The Knot (2x2)
    b.put(x, y, 0, palette.WHITE)
    b.put(x + dx, y, 0, palette.WHITE)
    b.put(x, y + dy, 0, palette.WHITE)
    b.put(x + dx, y + dy, 0, palette.WHITE)
    
    # The Fringe (Trailing threads)
    b.put(x + dx*2, y + dy*2, 0, palette.WHITE)
    b.put(x + dx*3, y + dy*2, 0, palette.BEIGE_LIGHT)
    b.put(x + dx*2, y + dy*3, 0, palette.BEIGE_LIGHT)
    b.put(x + dx*3, y + dy*3, 0, palette.WHITE)

def generate_tasseled_rug(width=40, depth=60):
    print(f"Weaving Ornate Rug with Corner Tassels ({width}x{depth})...")
    b = VoxelBuilder()
    
    half_w = width // 2
    half_d = depth // 2

    # Two primary colors
    primary = palette.FABRIC_RED
    accent = palette.FABRIC_GOLD

    # 1. Weave the main body
    for x in range(-half_w, half_w + 1):
        for y in range(-half_d, half_d + 1):
            color = primary
            
            # Main Border (Accent color)
            if abs(x) >= half_w - 3 or abs(y) >= half_d - 4:
                color = accent
                
            # Simple Diamond Medallion
            if abs(x) + abs(y) < 12:
                color = accent

            # Micro-Detail: Thread Texture (10% jitter)
            if random.random() < 0.10:
                if color == primary: color = palette.FABRIC_MAROON
                elif color == accent: color = palette.FABRIC_BURLAP
            
            b.put(x, y, 0, color)

    # 2. Add Detailed Corner Tassels
    # Top Right
    add_detailed_tassel(b, half_w, half_d, 1, 1)
    # Top Left
    add_detailed_tassel(b, -half_w, half_d, -1, 1)
    # Bottom Right
    add_detailed_tassel(b, half_w, -half_d, 1, -1)
    # Bottom Left
    add_detailed_tassel(b, -half_w, -half_d, -1, -1)

    # Save to JSON
    instructions = b.get_instructions()
    data = {"name": "ornate_rug", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/ornate_rug.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Rug woven with {len(b.voxels)} voxels.")

if __name__ == "__main__":
    generate_tasseled_rug()
