import json
import random

# Color Mapping from Palette
C_WOOD_DARK = 2
C_SKIN = 44 # Beige Light
C_CHARCOAL = 47
C_DEEP_RED = 48
C_DARK_GREY = 22 # Stone Dark as fallback/mantle
C_PURPLE_DARK = 49
C_MAGIC_PURPLE = 251
C_MAGIC_MAGENTA = 252
C_BOOK_COVER = 2 # Dark Wood

instructions = []

def add_box(x, y, z, w, d, h, color):
    instructions.append({
        "op": "add",
        "pos": [int(x), int(y), int(z)],
        "size": [int(w), int(d), int(h)],
        "color": int(color)
    })

def make_pyromancer():
    # --- 1. BASE / FEET ---
    # Blobby base
    add_box(-5, -4, 0, 10, 8, 2, C_CHARCOAL) 
    
    # --- 2. ROBES (Conical Taper) ---
    current_z = 2
    
    # Lower Robe (Wide)
    add_box(-6, -5, current_z, 12, 10, 6, C_CHARCOAL)
    
    # Mid Robe (Tapering)
    current_z += 6
    add_box(-5, -4, current_z, 10, 8, 8, C_CHARCOAL)
    
    # Upper Chest
    current_z += 8
    add_box(-4, -3, current_z, 8, 6, 7, C_CHARCOAL)
    chest_top_z = current_z + 7
    
    # SASH
    # Runs down center front (Y is approx -5 at bottom, -3 at top)
    # Split Bottom
    add_box(-3, -6, 2, 2, 1, 3, C_DEEP_RED) # Left Split
    add_box(1, -6, 2, 2, 1, 3, C_DEEP_RED)  # Right Split
    # Main Strip
    add_box(-1, -6, 4, 2, 1, chest_top_z - 4, C_DEEP_RED)

    # MANTLE (Shoulders)
    # Drapes over upper chest/arms
    add_box(-6, -4, chest_top_z - 3, 12, 8, 3, C_DARK_GREY) 
    
    # --- 3. HEAD & FACE ---
    head_z = chest_top_z 
    # Neck
    add_box(-2, -1, head_z, 4, 2, 1, C_SKIN)
    head_z += 1
    
    # Face Base (Skin) - Central block
    add_box(-3, -2, head_z, 6, 5, 7, C_SKIN)
    
    # HAIR (Helmet-like)
    # Top
    add_box(-4, -3, head_z + 6, 8, 8, 2, C_WOOD_DARK)
    # Back
    add_box(-4, 2, head_z, 8, 2, 8, C_WOOD_DARK)
    # Sides (sweeping back)
    add_box(-4, -2, head_z + 1, 1, 5, 6, C_WOOD_DARK) # Left Ear area
    add_box(3, -2, head_z + 1, 1, 5, 6, C_WOOD_DARK)  # Right Ear area
    
    # BEARD (Shovel Shape)
    # Starts at nose level, goes down to chest
    beard_top = head_z + 2
    # Main Mass
    add_box(-3, -3, head_z - 2, 6, 1, 5, C_WOOD_DARK) 
    # Tapered Bottom (on chest)
    add_box(-2, -4, head_z - 4, 4, 1, 2, C_WOOD_DARK)
    
    # EYES
    # Visible between hair and beard
    eye_z = head_z + 3
    add_box(-2, -3, eye_z, 1, 1, 1, C_CHARCOAL)
    add_box(1, -3, eye_z, 1, 1, 1, C_CHARCOAL)
    
    # --- 4. ARMS ---
    shoulder_z = chest_top_z - 2
    
    # RIGHT ARM (Hanging Down)
    r_arm_x = 5
    add_box(r_arm_x, -2, shoulder_z - 9, 3, 4, 9, C_CHARCOAL) # Sleeve
    add_box(r_arm_x, -2, shoulder_z - 9, 3, 4, 2, C_DEEP_RED)  # Cuff
    # Hand Peeking out
    add_box(r_arm_x+1, -1, shoulder_z - 11, 1, 2, 2, C_SKIN)  
    
    # LEFT ARM (Holding Book)
    l_arm_x = -8
    # Upper Arm
    add_box(l_arm_x, -2, shoulder_z - 5, 3, 4, 5, C_CHARCOAL)
    # Forearm (Angled forward)
    elbow_z = shoulder_z - 5
    add_box(l_arm_x, -6, elbow_z, 3, 6, 3, C_CHARCOAL)
    add_box(l_arm_x, -7, elbow_z, 3, 1, 3, C_DEEP_RED) # Cuff
    add_box(l_arm_x+1, -8, elbow_z+1, 1, 2, 2, C_SKIN) # Hand
    
    # --- 5. THE BOOK (Open V-Shape) ---
    # Hand is at roughly (-7, -8, elbow_z)
    book_base_x = l_arm_x
    book_base_y = -9
    book_base_z = elbow_z + 2
    
    # The 'V' is formed by two slabs meeting at the spine
    # Spine
    add_box(book_base_x+1, book_base_y, book_base_z, 1, 6, 1, C_BOOK_COVER)
    
    # Left Page (Angled Up-Left)
    # Step 1 (Low)
    add_box(book_base_x-1, book_base_y, book_base_z+1, 2, 6, 1, C_BOOK_COVER) # Cover
    add_box(book_base_x-1, book_base_y+1, book_base_z+2, 2, 4, 1, C_MAGIC_PURPLE) # Page
    # Step 2 (High)
    add_box(book_base_x-3, book_base_y, book_base_z+2, 2, 6, 1, C_BOOK_COVER) # Cover
    add_box(book_base_x-3, book_base_y+1, book_base_z+3, 2, 4, 1, C_MAGIC_PURPLE) # Page
    
    # Right Page (Angled Up-Right)
    # Step 1 (Low)
    add_box(book_base_x+2, book_base_y, book_base_z+1, 2, 6, 1, C_BOOK_COVER)
    add_box(book_base_x+2, book_base_y+1, book_base_z+2, 2, 4, 1, C_MAGIC_PURPLE)
    # Step 2 (High)
    add_box(book_base_x+4, book_base_y, book_base_z+2, 2, 6, 1, C_BOOK_COVER)
    add_box(book_base_x+4, book_base_y+1, book_base_z+3, 2, 4, 1, C_MAGIC_PURPLE)

    # --- 6. MAGIC PARTICLES ---
    # Cluster of small 1x1 cubes rising
    center_mx = book_base_x + 1.5
    center_my = book_base_y + 3
    center_mz = book_base_z + 4
    
    for _ in range(25): # More particles
        # Random offset in cone shape
        height = random.uniform(0, 12)
        spread = 1.5 + (height * 0.2) # Widens as it goes up
        
        mx = center_mx + random.uniform(-spread, spread)
        my = center_my + random.uniform(-spread, spread)
        mz = center_mz + height
        
        m_color = random.choice([C_MAGIC_PURPLE, C_MAGIC_MAGENTA])
        
        add_box(mx, my, mz, 1, 1, 1, m_color)

if __name__ == "__main__":
    make_pyromancer()
    
    data = {
        "name": "pyromancer",
        "instructions": instructions
    }
    
    with open("pyromancer.json", "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Generated {len(instructions)} instructions.")
