import sys
import json
import math
from PIL import Image
import palette

def get_closest_palette_index(r, g, b, a):
    if a < 128:
        return 0 # Transparent
    
    best_idx = 0
    min_dist = float('inf')
    
    # Palette indices 1 to 255
    for i in range(1, 256):
        pr, pg, pb, pa = palette.PALETTE_COLORS[i]
        
        # Skip fully transparent palette entries if the image pixel is opaque
        if pa == 0:
            continue
            
        # Euclidean distance
        dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        if dist < min_dist:
            min_dist = dist
            best_idx = i
            
    return best_idx

def image_to_csg(image_path, output_path, thickness=1, scale=1):
    print(f"Processing {image_path}...")
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    width, height = img.size
    instructions = []
    
    # We want the sprite to stand up (Z-up), so we map image Y to Z.
    # Image (0,0) is top-left.
    # World (0,0,0) will be bottom-left of the sprite.
    
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            color_idx = get_closest_palette_index(r, g, b, a)
            
            if color_idx > 0:
                # Invert Y so image bottom is at Z=0
                world_z = (height - 1 - y) * scale
                world_x = x * scale
                world_y = 0
                
                instructions.append({
                    "op": "add",
                    "pos": [world_x, world_y, world_z],
                    "size": [scale, thickness, scale],
                    "color": color_idx
                })

    # Derive asset name from output filename
    import os
    asset_name = os.path.splitext(os.path.basename(output_path))[0]

    csg_data = {
        "name": asset_name,
        "instructions": instructions
    }
    
    with open(output_path, 'w') as f:
        json.dump(csg_data, f, indent=2)
        
    print(f"Generated {len(instructions)} voxels. Saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python image_to_csg.py <input_image> <output_json> [thickness]")
    else:
        in_path = sys.argv[1]
        out_path = sys.argv[2]
        thk = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        image_to_csg(in_path, out_path, thk)
