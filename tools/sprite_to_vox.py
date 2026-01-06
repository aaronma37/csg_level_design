import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PIL import Image
import numpy as np
import palette

# Import VoxelModel
try:
    from csg_compiler import VoxelModel
except ImportError:
    print("Error: Could not import csg_compiler.")
    sys.exit(1)

def get_nearest_character_color(pixel_rgb):
    # Search range 100-149 in palette.PALETTE_COLORS
    best_dist = float('inf')
    best_idx = 100
    
    for i in range(100, 150):
        c = palette.PALETTE_COLORS[i]
        dr = int(c[0]) - int(pixel_rgb[0])
        dg = int(c[1]) - int(pixel_rgb[1])
        db = int(c[2]) - int(pixel_rgb[2])
        dist = dr*dr + dg*dg + db*db
        if dist < best_dist:
            best_dist = dist
            best_idx = i
    return best_idx

def convert_sprite_to_vox(image_path, output_path="character_sprite.vox", cell_size=64, index=0):
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found.")
        return

    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Error: Could not load image {e}")
        return

    w, h = img.size
    cols = w // cell_size
    row = index // cols
    col = index % cols
    
    x_start = col * cell_size
    y_start = row * cell_size
    
    sprite = img.crop((x_start, y_start, x_start + cell_size, y_start + cell_size))
    pixels = sprite.load()
    
    model = VoxelModel() 
    
    for y in range(cell_size):
        for x in range(cell_size):
            r, g, b, a = pixels[x, y]
            
            if a < 10: continue
            
            # Map to nearest character color (100-149)
            c_idx = get_nearest_character_color((r, g, b))
            
            vx = x - cell_size // 2
            vz = cell_size - 1 - y
            vy = 0 
            
            model.voxels[(vx, vy, vz)] = c_idx
                
    model.save(output_path)
    print(f"Saved {len(model.voxels)} voxels to {output_path} using palette indices 100-149.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to spritesheet")
    parser.add_argument("--out", default="character_sprite.vox")
    parser.add_argument("--index", type=int, default=0, help="Sprite index")
    args = parser.parse_args()
    
    convert_sprite_to_vox(args.image, args.out, index=args.index)