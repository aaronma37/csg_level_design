import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random
import math

# --- CONFIGURATION ---
# 1 Unit = 1 Voxel.
# Target Height: ~64 voxels.

# --- PALETTE ---
C_WOOD_DARK = 2
C_SKIN = 44 # Beige Light
C_CHARCOAL = 47
C_DEEP_RED = 48
C_DARK_GREY = 22
C_BOOK_COVER = 2
C_PURPLE_DARK = 49
C_MAGIC_PURPLE = 251
C_MAGIC_MAGENTA = 252

instructions = []

def add_voxel(x, y, z, color):
    instructions.append({
        "op": "add",
        "shape": "cuboid",
        "pos": [int(x), int(y), int(z)],
        "size": [1, 1, 1],
        "color": int(color)
    })

def add_box(x, y, z, w, d, h, color):
    instructions.append({
        "op": "add",
        "shape": "cuboid",
        "pos": [int(x), int(y), int(z)],
        "size": [int(w), int(d), int(h)],
        "color": int(color)
    })

def add_cylinder(cx, cy, base_z, radius, height, color):
    instructions.append({
        "op": "add",
        "shape": "cylinder",
        "pos": [int(cx), int(cy), int(base_z)],
        "radius": radius,
        "height": height,
        "axis": "z",
        "color": int(color)
    })

def add_tapered_cone(cx, cy, base_z, start_r, end_r, height, color):
    instructions.append({
        "op": "add",
        "shape": "cone",
        "pos": [int(cx), int(cy), int(base_z)],
        "radius_bottom": start_r,
        "radius_top": end_r,
        "height": height,
        "axis": "z",
        "color": int(color)
    })

def make_pyromancer_hd():
    # --- 1. BASE ---
    # Wide stance
    add_cylinder(0, 0, 0, 9, 2, C_CHARCOAL)
    
    # --- 2. ROBES (A-Line) ---
    # Wide Base (r=9) -> Narrow Chest (r=4.5)
    # Height ~40
    robe_height = 42
    add_tapered_cone(0, 0, 2, 9, 4.5, robe_height, C_CHARCOAL)
    
    # --- 3. SASH ---
    # Raised strip. Front is -Y.
    # We follow the slope of the cone.
    sash_width = 3
    for z in range(2, robe_height + 2):
        progress = (z - 2) / robe_height
        cone_radius = 9 + (4.5 - 9) * progress
        y_surf = -cone_radius
        
        add_box(-sash_width//2, y_surf-1, z, sash_width, 2, 1, C_DEEP_RED)

    # Sash Split at Bottom
    # Flaring out
    add_box(-sash_width//2 - 2, -10, 2, 2, 2, 5, C_DEEP_RED)
    add_box(sash_width//2 + 1, -10, 2, 2, 2, 5, C_DEEP_RED)

    # --- 4. MANTLE (Shoulders) ---
    # Wide block draping over arms.
    shoulder_z = 38
    # Main collar
    add_cylinder(0, 0, shoulder_z, 5, 5, C_DARK_GREY)
    # Shoulder pads extending out
    # Left
    add_box(-10, -5, shoulder_z-1, 8, 10, 4, C_DARK_GREY)
    # Right
    add_box(2, -5, shoulder_z-1, 8, 10, 4, C_DARK_GREY)
    # Back drape
    add_box(-6, 2, shoulder_z-6, 12, 4, 10, C_DARK_GREY)

    # --- 5. HEAD (Deconstructed) ---
    neck_z = shoulder_z + 5
    add_cylinder(0, 0, neck_z, 2.5, 2, C_SKIN)
    
    head_z = neck_z + 2
    # CORE HEAD (Skin Tone)
    add_box(-3.5, -4, head_z, 7, 7, 8, C_SKIN)
    
    # HAIR (Helmet Volume)
    # Wider than head
    add_box(-4.5, -4.5, head_z+6, 9, 9, 4, C_WOOD_DARK) # Top Cap
    add_box(-4.5, 1, head_z, 9, 4, 10, C_WOOD_DARK) # Back Mane
    # Sideburns / Temple Hair
    add_box(-4.5, -3, head_z+2, 1, 4, 6, C_WOOD_DARK)
    add_box(3.5, -3, head_z+2, 1, 4, 6, C_WOOD_DARK)

    # FACE DETAILS
    # Eyes (Pixels on skin)
    eye_z = head_z + 4
    add_box(-2, -4.1, eye_z, 1, 1, 1, C_CHARCOAL)
    add_box(2, -4.1, eye_z, 1, 1, 1, C_CHARCOAL)
    
    # BEARD (Shovel)
    beard_z = head_z + 1
    # Mustache Bar
    add_box(-3.5, -4.2, beard_z+1, 7, 1, 1, C_WOOD_DARK)
    # Main Beard Block
    add_box(-3.5, -4.5, beard_z - 3, 7, 2, 4, C_WOOD_DARK)
    # Shovel End (Chest)
    add_box(-2.5, -5, beard_z - 7, 5, 2, 4, C_WOOD_DARK)

    # --- 6. ARMS (Bell Sleeves) ---
    # Right Arm (Down)
    r_shoulder_x = 7
    r_shoulder_z_pos = shoulder_z + 2
    
    # Bell Sleeve: Narrow at shoulder (3), Wide at wrist (5)
    # Simulated with stacked boxes or cone logic? 
    # Let's do a vertical cone for the sleeve.
    sleeve_len = 14
    # Top radius 2, Bottom radius 3.5
    add_tapered_cone(r_shoulder_x, 0, r_shoulder_z_pos - sleeve_len, 3.5, 2, sleeve_len, C_CHARCOAL)
    
    # Red Cuff (Ring)
    add_cylinder(r_shoulder_x, 0, r_shoulder_z_pos - sleeve_len - 1, 4, 2, C_DEEP_RED)
    
    # Hand (Peeking out)
    add_box(r_shoulder_x-1, -1, r_shoulder_z_pos - sleeve_len - 4, 2, 2, 3, C_SKIN)


    # Left Arm (Holding Book)
    l_shoulder_x = -7
    # Upper Arm (Short)
    add_box(l_shoulder_x-2, -2, r_shoulder_z_pos - 4, 4, 4, 6, C_CHARCOAL)
    
    # Forearm (Forward & Wide)
    elbow_z = r_shoulder_z_pos - 4
    elbow_y = -2
    # Forearm as horizontal cone? Just a widening box.
    add_box(l_shoulder_x-2, elbow_y - 8, elbow_z, 5, 8, 5, C_CHARCOAL)
    
    # Cuff
    add_box(l_shoulder_x-2.5, elbow_y - 10, elbow_z-0.5, 6, 2, 6, C_DEEP_RED)
    
    # Hand (Gripping)
    hand_x = l_shoulder_x
    hand_y = elbow_y - 12
    hand_z = elbow_z + 1
    add_box(hand_x-1.5, hand_y, hand_z, 3, 3, 3, C_SKIN)

    # --- 7. BOOK (Chunky) ---
    book_x = hand_x
    book_y = hand_y - 2
    book_z = hand_z + 4 # Held slightly above hand/resting on thumb
    
    # Left Slab (Thick)
    # Cover
    add_box(book_x - 5, book_y, book_z + 2, 5, 8, 2, C_BOOK_COVER)
    # Pages
    add_box(book_x - 4, book_y+0.5, book_z + 4, 4, 7, 1, C_PURPLE_DARK)
    
    # Right Slab (Thick)
    # Cover
    add_box(book_x, book_y, book_z, 5, 8, 2, C_BOOK_COVER)
    # Pages
    add_box(book_x, book_y+0.5, book_z + 2, 4, 7, 1, C_PURPLE_DARK)
    
    # Spine Connector
    add_box(book_x - 1, book_y, book_z, 2, 8, 2, C_BOOK_COVER)

    # --- 8. MAGIC (Dense Cluster) ---
    center_mx = book_x
    center_my = book_y + 4
    center_mz = book_z + 5
    
    for _ in range(100): # Denser
        height = random.uniform(0, 18)
        # Wider spread at top
        radius = 1 + (height * 0.4)
        
        angle = random.uniform(0, 6.28)
        dist = random.uniform(0, radius)
        mx = center_mx + math.cos(angle) * dist
        my = center_my + math.sin(angle) * dist
        mz = center_mz + height
        
        # 3 Colors
        roll = random.random()
        if roll < 0.4: col = C_MAGIC_PURPLE
        elif roll < 0.8: col = C_MAGIC_MAGENTA
        else: col = C_PURPLE_DARK
        
        add_voxel(mx, my, mz, col)

if __name__ == "__main__":
    make_pyromancer_hd()
    
    data = {
        "name": "pyromancer_hd",
        "instructions": instructions
    }
    
    with open("../csg/pyromancer_hd.json", "w") as f:
        json.dump(data, f, indent=0)

