import cv2
import numpy as np

def analyze_sprite_content(image_path, cell_size=64):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("Error: Could not load image.")
        return

    # Extract first cell
    cell = img[0:cell_size, 0:cell_size]
    
    # Check Alpha
    if cell.shape[2] == 4:
        alpha = cell[:, :, 3]
        # Find non-transparent pixels
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)
        
        if np.any(rows):
            min_y, max_y = np.where(rows)[0][[0, -1]]
            height = max_y - min_y + 1
            print(f"Sprite Content Height: {height} pixels (Rows {min_y} to {max_y})")
        else:
            print("Sprite is empty.")
            
        if np.any(cols):
            min_x, max_x = np.where(cols)[0][[0, -1]]
            width = max_x - min_x + 1
            print(f"Sprite Content Width: {width} pixels (Cols {min_x} to {max_x})")
    else:
        print("Image has no alpha channel.")

if __name__ == "__main__":
    analyze_sprite_content("character_spritesheet.png")