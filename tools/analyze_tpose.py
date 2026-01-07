from PIL import Image
import sys

def analyze_sprite(path):
    img = Image.open(path).convert("RGBA")
    pixels = img.load()
    width, height = img.size
    
    # Check bounding box for different alpha thresholds
    for threshold in [1, 128, 250]:
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        found = False
        
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] >= threshold:
                    found = True
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        if found:
            print(f"Threshold Alpha >= {threshold}:")
            print(f"  Bounding Box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
            print(f"  Content Size: {max_x - min_x + 1}x{max_y - min_y + 1}")
            print(f"  Feet Y: {max_y}")
            print(f"  X-Center: {(min_x + max_x) / 2}")

if __name__ == "__main__":
    analyze_sprite("sprite_to_3d/t_pose_sprite.png")