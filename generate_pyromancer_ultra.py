import json
import random
import math

# --- CONFIGURATION ---
# Target Height: ~140 voxels (Ultra HD)
# Scale: roughly 2.5x the previous HD model.

# --- PALETTE ---
C_WOOD_DARK = 2
C_SKIN = 44 
C_SKIN_SHADOW = 45 # Darker beige
C_CHARCOAL = 47
C_CHARCOAL_LIGHT = 22 # Dark Grey for highlights
C_DEEP_RED = 48
C_RED_BRIGHT = 41
C_DARK_GREY = 22
C_BOOK_COVER = 2
C_PURPLE_DARK = 49
C_MAGIC_PURPLE = 251
C_MAGIC_MAGENTA = 252
C_GOLD = 241 # Fire Yellow as Gold

instructions = []

def add_voxel(x, y, z, color):
    instructions.append({
        "op": "add",
        "pos": [int(x), int(y), int(z)],
        "size": [1, 1, 1],
        "color": int(color)
    })

def add_box(x, y, z, w, d, h, color):
    instructions.append({
        "op": "add",
        "pos": [int(x), int(y), int(z)],
        "size": [int(w), int(d), int(h)],
        "color": int(color)
    })

def add_cylinder(cx, cy, base_z, radius, height, color):
    r2 = radius * radius
    for dz in range(int(height)):
        for dy in range(int(-radius), int(radius)+1):
            for dx in range(int(-radius), int(radius)+1):
                if dx*dx + dy*dy <= r2:
                    add_voxel(cx + dx, cy + dy, base_z + dz, color)

def add_sphere(cx, cy, cz, radius, color):
    r2 = radius * radius
    # Optimization: Bounding box
    ir = int(radius + 1)
    for dz in range(-ir, ir):
        for dy in range(-ir, ir):
            for dx in range(-ir, ir):
                if dx*dx + dy*dy + dz*dz <= r2:
                    add_voxel(cx + dx, cy + dy, cz + dz, color)

def add_ellipsoid(cx, cy, cz, rx, ry, rz, color):
    # x^2/a^2 + y^2/b^2 + z^2/c^2 <= 1
    irx, iry, irz = int(rx+1), int(ry+1), int(rz+1)
    for dz in range(-irz, irz):
        for dy in range(-iry, iry):
            for dx in range(-irx, irx):
                if (dx/rx)**2 + (dy/ry)**2 + (dz/rz)**2 <= 1.0:
                    add_voxel(cx + dx, cy + dy, cz + dz, color)

def make_pyromancer_ultra():
    # --- 1. BASE ---
    # Cylinder r=20, h=4
    # Add noise for rough ground?
    for x in range(-20, 21):
        for y in range(-20, 21):
            if x*x + y*y <= 400:
                h = 3 + random.randint(0, 1)
                for z in range(h):
                    add_voxel(x, y, z, C_CHARCOAL)

    # --- 2. ROBES (Volumetric Folds) ---
    # Height 0 to 90
    # Radius Base 18 -> Chest 9
    
    robe_height = 95
    for z in range(4, robe_height):
        prog = (z-4) / robe_height
        # Base Radius taper
        base_r = 18 * (1 - prog) + 9 * prog
        
        # Folds: Modulate radius with angle
        # 6 Folds around the circumference
        
        for deg in range(0, 360, 2): # 2 degree steps
            rad = math.radians(deg)
            # Sine wave for folds
            fold_mod = math.sin(rad * 6) * (1.5 * (1-prog)) # Folds deeper at bottom
            
            r = base_r + fold_mod
            
            # Convert to XY
            x = r * math.cos(rad)
            y = r * math.sin(rad)
            
            # Thickness of cloth (fill inward 2 voxels)
            add_voxel(x, y, z, C_CHARCOAL)
            add_voxel(x*0.95, y*0.95, z, C_CHARCOAL)
            add_voxel(x*0.9, y*0.9, z, C_CHARCOAL) # Solidify a bit

    # --- 3. SASH (Embroidered) ---
    # Follows the front contour (approx -Y)
    # Front is at angle -90 deg (270)
    # Let's map it roughly to x=0, y = -radius
    
    for z in range(4, robe_height):
        prog = (z-4) / robe_height
        base_r = 18 * (1 - prog) + 9 * prog
        # At front (270 deg), sin is -1.
        # Folds at 270: sin(270*6) = sin(1620) = sin(180) = 0.
        # So it's on a "peak" or "valley"? 
        # sin(6*theta). At theta=3pi/2 (-90). 6*3pi/2 = 9pi. sin(9pi) = 0.
        # It's a neutral point.
        
        y_surf = -(base_r) 
        
        # Sash Width 6
        for sx in range(-3, 4):
            # Stick out 1 voxel
            add_voxel(sx, y_surf-1, z, C_DEEP_RED)
            add_voxel(sx, y_surf-2, z, C_DEEP_RED)
            
            # Gold embroidery edges
            if sx == -3 or sx == 3:
                add_voxel(sx, y_surf-2, z, C_GOLD)

    # Sash Split
    # At z < 15, split outwards
    for z in range(4, 20):
        # Flare out
        off = (20 - z) * 0.4
        # Left tail
        add_voxel(-3 - off, -20, z, C_DEEP_RED)
        add_voxel(-4 - off, -20, z, C_DEEP_RED)
        # Right tail
        add_voxel(3 + off, -20, z, C_DEEP_RED)
        add_voxel(4 + off, -20, z, C_DEEP_RED)

    # --- 4. MANTLE (Detailed) ---
    shoulder_z = 88
    # Torus-like shape draped
    # Ellipse profile rotated?
    # Simple: Thick cylinder with ruffled bottom
    
    for z in range(shoulder_z - 10, shoulder_z + 4):
        # Radius expands as we go down (drape)
        drape = (shoulder_z + 4 - z) * 0.5
        r = 12 + drape
        
        for deg in range(0, 360, 4):
            rad = math.radians(deg)
            # Ruffles
            ruffle = math.sin(rad * 10) * 0.5
            final_r = r + ruffle
            
            x = final_r * math.cos(rad)
            y = final_r * math.sin(rad)
            
            add_voxel(x, y, z, C_DARK_GREY)
            add_voxel(x*0.95, y*0.95, z, C_DARK_GREY)

    # --- 5. HEAD (Sculpted) ---
    neck_z = shoulder_z + 4
    # Neck
    add_cylinder(0, 0, neck_z, 4, 4, C_SKIN)
    
    head_z = neck_z + 4
    head_cy = 120 # Center of head Z
    # Ellipsoid Head
    add_ellipsoid(0, 0, head_z + 8, 7, 8, 9, C_SKIN)
    
    # FACE FEATURES
    face_y = -7
    nose_z = head_z + 6
    # Nose (Triangle prism ish)
    for nz in range(0, 4):
        add_voxel(0, face_y - nz*0.5, nose_z + nz, C_SKIN_SHADOW)
        add_voxel(-1, face_y, nose_z + nz, C_SKIN)
        add_voxel(1, face_y, nose_z + nz, C_SKIN)
        
    # Eye Sockets (Recessed)
    # We carve out? Or just paint dark pixels
    eye_z = head_z + 9
    add_voxel(-3, face_y+1, eye_z, C_CHARCOAL)
    add_voxel(3, face_y+1, eye_z, C_CHARCOAL)
    # Brows
    add_voxel(-3, face_y, eye_z+1, C_WOOD_DARK)
    add_voxel(-2, face_y, eye_z+1, C_WOOD_DARK)
    add_voxel(3, face_y, eye_z+1, C_WOOD_DARK)
    add_voxel(2, face_y, eye_z+1, C_WOOD_DARK)

    # HAIR (Strands)
    # Generate curves for hair
    # Top helmet
    for i in range(200):
        # Random start point on top of head
        theta = random.uniform(0, 6.28)
        r = random.uniform(0, 7)
        sx = r * math.cos(theta)
        sy = r * math.sin(theta)
        sz = head_z + 16
        
        # Drop down
        length = random.randint(15, 25)
        curr_x, curr_y, curr_z = sx, sy, sz
        
        for j in range(length):
            add_voxel(curr_x, curr_y, curr_z, C_WOOD_DARK)
            # Move down and slightly out
            curr_z -= 1
            curr_x += random.uniform(-0.2, 0.2)
            curr_y += random.uniform(-0.2, 0.2)
            # Push out if hitting head? Simplified: just let it clip or flow back
            if curr_y > 0: curr_y += 0.1 # Flow back
            
    # BEARD (Volumetric)
    # Start at chin/cheeks
    for x in range(-7, 8):
        for z_b in range(head_z, head_z+5):
            # On surface of face
             if x*x <= 49:
                y = -math.sqrt(49 - x*x)
                if y < -3: # Front face
                    # Grow hair outwards/down
                    hair_len = random.randint(10, 20)
                    cx, cy, cz = x, y, z_b
                    for k in range(hair_len):
                        add_voxel(cx, cy, cz, C_WOOD_DARK)
                        cz -= 1
                        cy -= 0.2 # Angle out
                        cx += random.uniform(-0.1, 0.1)

    # --- 6. ARMS (Articulated) ---
    r_shoulder_x = 14
    r_shoulder_z = shoulder_z - 2
    
    # RIGHT ARM (Bell Sleeve)
    # Elbow
    elbow_z = r_shoulder_z - 15
    # Upper Arm
    for z in range(elbow_z, r_shoulder_z):
        add_voxel(r_shoulder_x, 0, z, C_CHARCOAL)
        add_sphere(r_shoulder_x, 0, z, 4, C_CHARCOAL)
        
    # Forearm/Sleeve widening
    wrist_z = elbow_z - 15
    for z in range(wrist_z, elbow_z):
        prog = (elbow_z - z) / 15
        r = 4 + 4*prog # Widen to 8
        add_sphere(r_shoulder_x, 0, z, r, C_CHARCOAL)
        
    # Red Cuff
    add_sphere(r_shoulder_x, 0, wrist_z, 5, C_DEEP_RED)
    
    # Right Hand (Fingers)
    hand_z = wrist_z - 4
    add_box(r_shoulder_x-2, -2, hand_z, 4, 4, 4, C_SKIN)
    # Fingers (hanging)
    for f in range(5):
        fx = r_shoulder_x - 2 + f
        for fz in range(1, 4):
            add_voxel(fx, -1, hand_z - fz, C_SKIN)


    # LEFT ARM (Holding Book)
    l_shoulder_x = -14
    
    # Upper
    l_elbow_z = r_shoulder_z - 12
    l_elbow_y = -5
    # Draw line from shoulder to elbow
    # ... approximated by spheres
    add_sphere(l_shoulder_x, 0, r_shoulder_z, 5, C_CHARCOAL)
    add_sphere(l_shoulder_x, l_elbow_y, l_elbow_z, 4.5, C_CHARCOAL)
    
    # Forearm (Forward to book)
    wrist_x = l_shoulder_x
    wrist_y = -25
    wrist_z = l_elbow_z + 5
    
    # Interpolate Forearm
    steps = 20
    for i in range(steps):
        t = i / steps
        cx = l_shoulder_x
        cy = l_elbow_y * (1-t) + wrist_y * t
        cz = l_elbow_z * (1-t) + wrist_z * t
        r = 4 + 2*t # Bell sleeve widening
        add_sphere(cx, cy, cz, r, C_CHARCOAL)
        
    # Cuff
    add_sphere(wrist_x, wrist_y, wrist_z, 5, C_DEEP_RED)
    
    # Hand (Gripping)
    # Palm
    add_box(wrist_x-2, wrist_y-2, wrist_z, 4, 4, 4, C_SKIN)
    # Fingers wrapping up
    for f in range(4):
        fx = wrist_x - 1.5 + f
        add_voxel(fx, wrist_y-3, wrist_z+2, C_SKIN) # Finger tip

    # --- 7. BOOK (Ultra HD) ---
    book_cx = wrist_x
    book_cy = wrist_y - 2
    book_cz = wrist_z + 6
    
    # Angled slabs
    # Use vectors to place voxels?
    # Left Slab: Rotated 30 deg left
    # Right Slab: Rotated 30 deg right
    
    w, h, thick = 12, 18, 3 # Book dims
    
    for iy in range(h):
        for ix in range(w):
            for iz in range(thick):
                # Local coords
                lx = -ix
                ly = iy - h/2
                lz = iz
                
                # Rotate Left Slab (-30 deg around Y axis)
                # x' = x cos - z sin
                # z' = x sin + z cos
                angle = math.radians(-30)
                rx = lx * math.cos(angle) - lz * math.sin(angle)
                rz = lx * math.sin(angle) + lz * math.cos(angle)
                
                # Color: Cover (bottom), Page (top)
                col = C_BOOK_COVER if iz < 1 else C_PURPLE_DARK
                # Add Noise for Runes
                if iz == thick-1 and random.random() < 0.2:
                    col = C_MAGIC_MAGENTA
                
                add_voxel(book_cx + rx, book_cy + ly, book_cz + rz, col)

                # Right Slab (+30 deg)
                lx = ix
                rx = lx * math.cos(-angle) - lz * math.sin(-angle)
                rz = lx * math.sin(-angle) + lz * math.cos(-angle)
                add_voxel(book_cx + rx, book_cy + ly, book_cz + rz, col)

    # --- 8. MAGIC (Particle System) ---
    # Rising spiral?
    center_mz = book_cz + 5
    for i in range(200):
        t = i / 200.0
        height = t * 30
        radius = 2 + t * 10
        angle = t * 20 # Spiral
        
        mx = book_cx + math.cos(angle) * radius + random.uniform(-2, 2)
        my = book_cy + math.sin(angle) * radius + random.uniform(-2, 2)
        mz = center_mz + height
        
        col = C_MAGIC_PURPLE if i % 2 == 0 else C_MAGIC_MAGENTA
        add_voxel(mx, my, mz, col)

if __name__ == "__main__":
    make_pyromancer_ultra()
    
    data = {
        "name": "pyromancer_ultra",
        "instructions": instructions
    }
    
    with open("pyromancer_ultra.json", "w") as f:
        json.dump(data, f, indent=0)
