import sys
from PIL import Image
import palette

# Load palette colors for analysis
PALETTE_MAP = {}
for i in range(1, 256):
    PALETTE_MAP[i] = palette.PALETTE_COLORS[i]

def get_closest_palette_index(r, g, b, a):
    if a < 128: return 0
    best_idx = 0
    min_dist = float('inf')
    for i, color in PALETTE_MAP.items():
        pr, pg, pb, pa = color
        if pa == 0: continue
        dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        if dist < min_dist:
            min_dist = dist
            best_idx = i
    return best_idx

def analyze_image(path, target_height):
    try:
        img = Image.open(path).convert("RGBA")
    except Exception as e:
        print(f"Error: {e}")
        return

    # Resize
    w, h = img.size
    aspect = w / h
    new_h = target_height
    new_w = int(new_h * aspect)
    img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
    
    print(f"Original Size: {w}x{h}")
    print(f"Resized Size: {new_w}x{new_h}")
    
    # Analyze histogram
    pixels = img.load()
    color_counts = {}
    
    grid = []
    
    for y in range(new_h):
        row = []
        for x in range(new_w):
            r, g, b, a = pixels[x, y]
            idx = get_closest_palette_index(r, g, b, a)
            row.append(idx)
            
            if idx > 0:
                color_counts[idx] = color_counts.get(idx, 0) + 1
        grid.append(row)

    print("\n--- DOMINANT COLORS ---")
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    for idx, count in sorted_colors[:10]:
        r, g, b, a = PALETTE_MAP.get(idx, (0,0,0,0))
        print(f"Color {idx}: {count} pixels (RGB: {r},{g},{b})")

    print("\n--- ASCII PREVIEW ---")
    # Simple ASCII mapping for visualization
    # 0 = space
    # 1-20 (Wood) = #
    # 21-40 (Stone) = =
    # 41-50 (Colors) = *
    # Others = ?
    
    for y in range(new_h):
        line = ""
        for x in range(new_w):
            idx = grid[y][x]
            if idx == 0: char = "."
            elif 1 <= idx <= 20: char = "#" # Wood
            elif 21 <= idx <= 40: char = "=" # Stone
            elif 41 <= idx <= 43: char = "X" # RGB
            elif 240 <= idx <= 255: char = "!" # Fire
            else: char = "@" # Beige/Other
            line += char
        print(f"{y:02d}: {line}")

if __name__ == "__main__":
    analyze_image("sprite_example.png", 55)
