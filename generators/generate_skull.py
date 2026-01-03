import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from tools.builder import VoxelBuilder
import palette

def generate_skull():
    print("Generating Skull using VoxelBuilder (Logical Placement)...")
    b = VoxelBuilder()

    # 1. BRAIN CASE (Cranium)
    # Main mass: X:0-4, Y:-3-3, Z:3-10
    b.fill(0, -3, 3, 4, 3, 10, palette.BEIGE_MEDIUM)
    
    # 2. JAW & FACE
    # Lower jaw: X:0-3, Y:1-3, Z:0-2
    b.fill(0, 1, 0, 3, 3, 2, palette.BEIGE_MEDIUM)
    # Upper face/Maxilla: X:0-4, Y:2-4, Z:3-5
    b.fill(0, 2, 3, 4, 4, 5, palette.BEIGE_MEDIUM)

    # 3. CARVING FEATURES (Depth)
    # Eye Socket: X:2, Y:3-4, Z:6-8
    b.carve(1, 3, 6, 3, 4, 8)
    # Nasal Cavity: X:0-1, Y:4, Z:4-5
    b.carve(0, 3, 4, 1, 4, 5)
    
    # 4. ADDING SHADOWS & DETAILS
    # Socket Lining
    b.put(1, 2, 6, palette.BEIGE_DARK)
    b.put(3, 2, 6, palette.BEIGE_DARK)
    b.put(2, 2, 8, palette.BEIGE_DARK)

    # 5. MAGICAL EYES (Centered in the carved sockets)
    # Eye Core
    b.put(2, 3, 7, palette.PURPLE_GLOW)
    # Eye Aura (Ghost) - Offset so it doesn't touch X=0
    b.put(3, 4, 7, palette.GHOST_PURPLE)
    b.put(2, 4, 8, palette.GHOST_PURPLE)
    b.put(2, 4, 6, palette.GHOST_PURPLE)

    # 6. TEETH
    b.put(1, 4, 2, palette.BEIGE_LIGHT)
    b.put(3, 4, 2, palette.BEIGE_LIGHT)

    # 7. FINALIZE (Mirror to the left)
    b.mirror_x()

    # Save to JSON
    instructions = b.get_instructions()
    data = {"name": "skull", "instructions": instructions}
    
    output_path = os.path.join(os.path.dirname(__file__), "../csg/skull.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Created logical skull with {len(b.voxels)} voxels.")

if __name__ == "__main__":
    generate_skull()
