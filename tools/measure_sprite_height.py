from PIL import Image
import os

def measure_sprite_height(image_path, tile_size=64):
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Crop the first tile (top-left)
    # Assuming the spritesheet starts at 0,0
    sprite = img.crop((0, 0, tile_size, tile_size))
    
    # Get bounding box of non-zero alpha pixels
    bbox = sprite.getbbox()
    
    if not bbox:
        print("Error: Sprite is fully transparent.")
        return

    left, top, right, bottom = bbox
    height = bottom - top
    width = right - left
    
    print(f"Sprite Analysis for '{image_path}':")
    print(f"  First Tile: {tile_size}x{tile_size}")
    print(f"  Visible Content BBox: {bbox}")
    print(f"  Visible Height: {height} pixels")
    print(f"  Visible Width: {width} pixels")
    print(f"  Vertical Offset (from top): {top}")

if __name__ == "__main__":
    # Path relative to project root
    path = "textures/character_spritesheet.png"
    if os.path.exists(path):
        measure_sprite_height(path)
    else:
        # Fallback to the one found in voxel_reconstruction if main one missing
        path = "voxel_reconstruction/character_spritesheet.png"
        if os.path.exists(path):
            measure_sprite_height(path)
        else:
            print(f"File not found: {path}")
