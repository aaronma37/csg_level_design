import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
from PIL import Image
import json
import palette

# --- CONFIGURATION ---
TARGET_HEIGHT = 55
BACKGROUND_COLOR_IDX = 44 # Beige Light (from analysis)
SCALE = 1 # Voxel size per pixel

# Depth Configuration (How thick is each material?)
# Centered around relative Y=0.
# (Thickness, Offset) -> The voxel will spawn from (Offset) to (Offset + Thickness)
# We want the "Body" to be central.
# Body: Thick 4, Offset 0 -> [0, 1, 2, 3]
# Armor: Thick 6, Offset -1 -> [-1, 0, 1, 2, 3, 4] (Wraps body)
# Detail: Thick 2, Offset -2 -> [-2, -1] (Sticks out front) -> Wait, logic check.
# Let's align to Center Line.
# Body Center = 2.
# Body (4): 0 to 4.
# Armor (6): -1 to 5.
# Detail (2): -2 to 0 (Back) or 4 to 6 (Front)? Usually details are on front.
# Let's assume the sprite is facing "South" (towards camera).
# So "Front" is lower Y (or higher Y depending on coordinate system).
# In MagicaVoxel, Z is up. Y is usually depth.
# Let's say -Y is Front.
# Body: Y=[-2, 2] (Thick 4)
# Armor: Y=[-3, 3] (Thick 6)
# Detail: Y=[-4, -2] (Thick 2, in front)

TYPE_DEPTHS = {
    "wood":  {"thick": 4, "offset": -2}, # Base Body
    "stone": {"thick": 6, "offset": -3}, # Armor/Outer
    "misc":  {"thick": 2, "offset": -4}, # Details (popping out front)
    "fire":  {"thick": 4, "offset": -2}, # Standard
    "default":{"thick": 4, "offset": -2}
}

def get_material_type(idx):
    if 1 <= idx <= 20: return "wood"
    if 21 <= idx <= 40: return "stone"
    if 240 <= idx <= 255: return "fire"
    if idx in [41, 42, 43]: return "misc" # Red/Green/Blue
    return "default"

def get_closest_palette_index(r, g, b, a):
    if a < 128: return 0
    best_idx = 0
    min_dist = float('inf')
    for i in range(1, 256):
        pr, pg, pb, pa = palette.PALETTE_COLORS[i]
        if pa == 0: continue
        dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        if dist < min_dist:
            min_dist = dist
            best_idx = i
    return best_idx

def generate_figurine(image_path, output_json):
    print(f"Generating 3D Figurine from {image_path}...")
    
    # 1. Load and Resize
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    aspect = w / h
    new_h = TARGET_HEIGHT
    new_w = int(new_h * aspect)
    img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
    pixels = img.load()
    
    instructions = []
    
    # 2. Iterate Pixels
    # Image Y goes Top->Bottom. World Z goes Bottom->Top.
    for y in range(new_h):
        world_z = (new_h - 1 - y) * SCALE
        
        for x in range(new_w):
            r, g, b, a = pixels[x, y]
            idx = get_closest_palette_index(r, g, b, a)
            
            # Skip Transparent or Background Color
            if idx == 0 or idx == BACKGROUND_COLOR_IDX:
                continue
                
            mat_type = get_material_type(idx)
            props = TYPE_DEPTHS[mat_type]
            
            thickness = props["thick"]
            y_start = props["offset"]
            
            # Special Logic: Held Item (Right Side cluster)
            # Rough heuristic: If X > new_w * 0.65 and Y in middle rows
            # It's likely an item. Push it forward.
            if x > new_w * 0.65 and 10 < y < 40:
                y_start -= 2 # Push forward by 2 units
            
            instructions.append({
                "op": "add",
                "pos": [x * SCALE, y_start, world_z],
                "size": [SCALE, thickness, SCALE],
                "color": idx
            })

    # 3. Save
    asset_name = "figurine_hero"
    data = {
        "name": asset_name,
        "instructions": instructions
    }
    
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(instructions)} voxel instructions to {output_json}")

if __name__ == "__main__":
    generate_figurine("../textures/sprite_example.png", "../csg/figurine_hero.json")
