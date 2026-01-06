import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import math
from PIL import Image
from tools.builder import VoxelBuilder
import palette

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

def sync_sprite_palette(pixels, w, h):
    # Find up to 20 unique colors
    unique_colors = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 128: continue
            if (r + g + b) < 50: continue # Ignore near-black shadows
            c = (r, g, b)
            if c not in unique_colors and len(unique_colors) < 20:
                unique_colors.append(c)
    
    with open("palette.py", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        if "# --- SPRITE WORKSPACE (150-199) ---" in line:
            new_lines.append(line)
            new_lines.append("# Reserved for active sprite prototyping.\n")
            for i, c in enumerate(unique_colors):
                new_lines.append(f"set_color({150+i}, {c[0]}, {c[1]}, {c[2]})\n")
            skip = True
        elif skip and "# ---" in line:
            skip = False
            new_lines.append("\n")
            new_lines.append(line)
        elif not skip:
            new_lines.append(line)
            
    with open("palette.py", "w") as f:
        f.writelines(new_lines)
    
    print(f"Synced {len(unique_colors)} colors to palette.py (150-169)")
    return unique_colors

def generate_character(sprite_path, output_json, sprite_index=0):
    print(f"Generating Character from {sprite_path} (Index {sprite_index})...")
    
    # Clean up stale artifacts
    if os.path.exists(output_json): os.remove(output_json)
    
    # 1. Load Sprite
    try:
        img = Image.open(sprite_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Assuming 64x64 sprites
    SPRITE_SIZE = 64
    cols = img.width // SPRITE_SIZE
    row = sprite_index // cols
    col = sprite_index % cols
    
    x_off = col * SPRITE_SIZE
    y_off = row * SPRITE_SIZE
    
    # Crop and Save for Critic
    sprite = img.crop((x_off, y_off, x_off + SPRITE_SIZE, y_off + SPRITE_SIZE))
    sprite.save("target_sprite.png")
    pixels = sprite.load()
    
    # Sync Palette
    sprite_colors = sync_sprite_palette(pixels, SPRITE_SIZE, SPRITE_SIZE)
    # Reload palette
    import importlib
    importlib.reload(palette)
    
    # --- 1. GEOMETRIC ANALYSIS ---
    # Find bounding box
    min_y, max_y = SPRITE_SIZE, 0
    min_x, max_x = SPRITE_SIZE, 0
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            if pixels[x, y][3] > 128:
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                if x < min_x: min_x = x
                if x > max_x: max_x = x
    
    pixel_height = max_y - min_y + 1
    pixel_width = max_x - min_x + 1
    
    # Chibi Ratios: Big head, stout body
    head_h = int(pixel_height * 0.45)
    torso_h = int(pixel_height * 0.30)
    leg_h = pixel_height - head_h - torso_h

    # --- 2. COLOR SAMPLING (Using Sprite Workspace) ---
    def get_best_sprite_idx(start_x, start_y, w, h, ignore_indices=[]):
        counts = {}
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                if x < 0 or x >= SPRITE_SIZE or y < 0 or y >= SPRITE_SIZE: continue
                r, g, b, a = pixels[x, y]
                if a < 128: continue
                if (r + g + b) < 50: continue # Ignore near-black shadows
                idx = get_closest_palette_index(r, g, b, a)
                if idx in ignore_indices: continue
                counts[idx] = counts.get(idx, 0) + 1
        if not counts: return None
        return max(counts, key=counts.get)

    lower_idx = get_best_sprite_idx(min_x, min_y + head_h + torso_h, pixel_width, leg_h) or 2
    torso_idx = get_best_sprite_idx(min_x, min_y + head_h, pixel_width, torso_h) or 1
    
    # Find Skin tone (Dominant in center of head area)
    head_idx = get_best_sprite_idx(min_x + pixel_width//4, min_y + 2, pixel_width//2, head_h - 2, ignore_indices=[torso_idx, lower_idx, 6]) or 100
    
    # Find Item (Viewer Right)
    item_idx = get_best_sprite_idx(min_x + int(pixel_width*0.7), min_y + head_h, int(pixel_width*0.3), torso_h, ignore_indices=[torso_idx]) or 0
    has_item = item_idx != 0 and item_idx != torso_idx
    
    # Find Beard (Distinct from head/torso)
    beard_idx = get_best_sprite_idx(min_x, min_y + int(head_h*0.5), pixel_width, int(head_h*0.5), ignore_indices=[head_idx, torso_idx, 6]) or 0
    has_beard = beard_idx != 0 and beard_idx != head_idx

    # Find Arms
    arms_idx = get_best_sprite_idx(min_x, min_y + head_h, int(pixel_width*0.2), torso_h) or torso_idx

    # --- 3. VOXEL CONSTRUCTION (High Quality Chibi) ---
    b = VoxelBuilder()
    
    # Ratios
    h_head = int(pixel_height * 0.50)
    h_torso = int(pixel_height * 0.30)
    h_legs = pixel_height - h_head - h_torso
    
    # 1. FACADE (Exact Sprite at Y=0 and thick edge at Y=1)
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 128: continue
            
            c_idx = get_closest_palette_index(red, green, blue, alpha)
            vx = x - (min_x + pixel_width//2)
            vz = (max_y - y)
            
            b.put(vx, 0, vz, c_idx) # Front face
            b.put(vx, 1, vz, c_idx) # Side thickness

    # 2. LOGICAL VOLUME (Behind the facade at Y=2 to Y=10)
    # This provides the 'heft' without messing up the front colors.
    w_body = int(pixel_width * 0.45)
    w_head = int(pixel_width * 0.50)
    max_depth = 10
    
    # Head Volume (A rounded cube behind the face)
    z_head_start = h_legs + h_torso
    b.fill(-w_head, 2, z_head_start, w_head, max_depth, pixel_height, head_idx)
    
    # Torso Volume
    b.fill(-w_body, 2, h_legs, w_body, max_depth - 2, z_head_start, torso_idx)
    
    # Robe Flare (Widens at bottom)
    for z in range(h_legs + 1):
        flare = (h_legs - z) // 2
        wf = w_body + flare
        b.fill(-wf, 2, z, wf, max_depth - 2, z, lower_idx)
        
    # Beard (Sits slightly in front of the facade Y=0)
    if has_beard:
        # We put it at Y=-1 and Y=-2 to make it pop
        b.fill(-w_head+2, -2, z_head_start - 4, w_head-2, -1, z_head_start + 4, beard_idx)

    # Item (Book) - Extruded and Visible
    if has_item:
        ix = w_body + 2
        b.fill(ix, -4, h_legs + 4, ix + 6, 2, h_legs + 12, item_idx)
        b.put(ix + 3, -5, h_legs + 8, palette.PURPLE_GLOW)

    # 4. Save
    instructions = b.get_instructions()
    data = {
        "name": "character_logical",
        "instructions": instructions
    }
    
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved High-Quality Chibi model to {output_json}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to spritesheet")
    parser.add_argument("--out", default="csg/character.json")
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    
    generate_character(args.image, args.out, args.index)
