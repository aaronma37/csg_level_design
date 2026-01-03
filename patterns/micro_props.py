from tools.builder import VoxelBuilder
import palette
import math

def make_skull(glow_color=None):
    """Returns a VoxelBuilder containing a centered 8x10 skull."""
    b = VoxelBuilder()
    glow = glow_color if glow_color else palette.PURPLE_GLOW
    b.fill(0, -3, 3, 4, 3, 10, palette.BEIGE_MEDIUM)
    b.fill(0, 1, 0, 3, 3, 2, palette.BEIGE_MEDIUM)
    b.fill(0, 2, 3, 4, 4, 5, palette.BEIGE_MEDIUM)
    b.carve(1, 3, 6, 3, 4, 8); b.carve(0, 3, 4, 1, 4, 5)
    b.put(1, 2, 6, palette.BEIGE_DARK); b.put(3, 2, 6, palette.BEIGE_DARK); b.put(2, 2, 8, palette.BEIGE_DARK)
    b.put(2, 3, 7, glow); b.put(3, 4, 7, palette.GHOST_PURPLE); b.put(2, 4, 8, palette.GHOST_PURPLE); b.put(2, 4, 6, palette.GHOST_PURPLE)
    b.put(1, 4, 2, palette.BEIGE_LIGHT); b.put(3, 4, 2, palette.BEIGE_LIGHT)
    b.mirror_x()
    return b

def make_plaque(width=12, height=16):
    """Returns a wooden plaque for mounting trophies."""
    b = VoxelBuilder()
    hw, hh = width // 2, height // 2
    b.fill(-hw, 0, -hh, hw, 1, hh, palette.WOOD_BROWN)
    b.fill(-hw, 0, -hh, hw, 1, -hh, palette.WOOD_DARK); b.fill(-hw, 0, hh, hw, 1, hh, palette.WOOD_DARK)
    b.fill(-hw, 0, -hh, -hw, 1, hh, palette.WOOD_DARK); b.fill(hw, 0, -hh, hw, 1, hh, palette.WOOD_DARK)
    return b

def make_weapon_rack_frame(width=32, height=28):
    """Returns a doubled wooden frame for holding weapons."""
    b = VoxelBuilder()
    hw = width // 2
    b.fill(-hw, 0, 0, -hw+3, 4, height, palette.WOOD_DARK)
    b.fill(hw-3, 0, 0, hw, 4, height, palette.WOOD_DARK)
    b.fill(-hw, 0, 4, hw, 2, 6, palette.WOOD_BROWN)
    b.fill(-hw, 0, height-8, hw, 2, height-6, palette.WOOD_BROWN)
    b.fill(-hw-2, -4, 0, -hw+4, 8, 2, palette.WOOD_DARK)
    b.fill(hw-4, -4, 0, hw+2, 8, 2, palette.WOOD_DARK)
    return b

def make_shortsword():
    """Returns a detailed 2x24 shortsword."""
    b = VoxelBuilder()
    # Blade
    b.fill(0, 0, 8, 1, 1, 22, palette.STONE_LIGHT)
    # Blood Groove (Fuller)
    b.fill(0, 1, 9, 1, 1, 20, palette.STONE_DARK)
    # Crossguard (Chamfered look)
    b.fill(-3, 0, 6, 4, 1, 7, palette.FIRE_CORE)
    b.put(-3, 0, 7, 0); b.put(4, 0, 7, 0) # Carve tips
    # Hilt with pommel
    b.fill(0, 0, 3, 1, 1, 5, palette.WOOD_DARK)
    b.fill(-1, 0, 1, 2, 1, 2, palette.FIRE_CORE) # Pommel
    return b

def make_battleaxe():
    """Returns a detailed battleaxe."""
    b = VoxelBuilder()
    # Shaft with leather grip
    b.fill(0, 0, 0, 1, 1, 20, palette.WOOD_DARK)
    b.fill(0, 0, 5, 1, 1, 10, palette.WOOD_BROWN) # Grip
    # Axe Head (Chamfered edge)
    b.fill(2, 0, 14, 4, 1, 20, palette.STONE_BASE)
    b.fill(4, 0, 15, 4, 1, 19, palette.STONE_LIGHT) # Sharpened edge
    b.fill(-3, 0, 14, -1, 1, 20, palette.STONE_BASE)
    b.fill(-3, 0, 15, -3, 1, 19, palette.STONE_LIGHT) # Sharpened edge
    # Top Spike
    b.fill(0, 0, 21, 1, 1, 23, palette.STONE_LIGHT)
    return b

def make_spear():
    """Returns a detailed spear."""
    b = VoxelBuilder()
    # Shaft with multiple grips
    b.fill(0, 0, 0, 1, 1, 26, palette.WOOD_DARK)
    for z in [5, 6, 15, 16]:
        b.fill(0, 0, z, 1, 1, z, palette.WOOD_BROWN)
    # Tip (Ornate)
    b.fill(0, 0, 27, 1, 1, 30, palette.STONE_LIGHT)
    b.fill(-2, 0, 26, 3, 1, 26, palette.STONE_BASE)
    b.put(0, 0, 26, palette.FIRE_CORE) # Gold binding
    return b

def make_sturdy_chair():
    """Returns a correctly scaled wooden chair (0.25 CU seat height)."""
    b = VoxelBuilder()
    
    # 1. Legs (4 corner posts, slightly tapered at the bottom)
    # Front Left
    b.fill(-7, -7, 0, -6, -6, 12, palette.WOOD_DARK)
    # Front Right
    b.fill(6, -7, 0, 7, -6, 12, palette.WOOD_DARK)
    # Back Left
    b.fill(-7, 6, 0, -6, 7, 28, palette.WOOD_DARK) # Extends to backrest
    # Back Right
    b.fill(6, 6, 0, 7, 7, 28, palette.WOOD_DARK) # Extends to backrest
    
    # 2. Seat Base
    b.fill(-7, -7, 12, 7, 7, 13, palette.WOOD_BROWN)
    # Seat Cushion (Micro-detail)
    b.fill(-6, -6, 14, 6, 6, 14, palette.WOOD_LIGHT)
    
    # 3. Backrest Rails
    b.fill(-6, 7, 20, 6, 7, 22, palette.WOOD_BROWN)
    b.fill(-6, 7, 26, 6, 7, 28, palette.WOOD_BROWN)
    # Central vertical slat
    b.fill(-1, 7, 14, 1, 7, 28, palette.WOOD_BROWN)
    
    return b

def make_candle(height=5):
    """Returns a simple candle with a glowing flame and a metal base."""
    b = VoxelBuilder()
    # Metal Holder Base
    b.fill(-1, -1, 0, 2, 2, 0, palette.STONE_DARK)
    b.put(0, 0, 1, palette.STONE_DARK)
    b.put(1, 0, 1, palette.STONE_DARK)
    b.put(0, 1, 1, palette.STONE_DARK)
    b.put(1, 1, 1, palette.STONE_DARK)
    
    # Wax body (offset by 2v to sit in the holder)
    b.fill(0, 0, 2, 1, 1, height+1, palette.WHITE)
    # Wick
    b.put(0, 0, height+2, palette.STONE_DARK)
    # Flame (Emissive)
    b.put(0, 0, height+3, palette.FIRE_GLOW)
    return b

def make_barrel(radius=8, height=22):
    """Returns a wooden barrel with iron hoops."""
    b = VoxelBuilder()
    
    # 1. Main Body (Vertical Planks)
    for angle in range(0, 360, 2):
        rad = math.radians(angle)
        # Bulge the middle slightly
        for z in range(height):
            # Sine bulge: max at middle, min at ends
            bulge = math.sin((z / height) * 3.14159) * 1.5
            r = radius + bulge
            x = int(round(math.cos(rad) * r))
            y = int(round(math.sin(rad) * r))
            
            # Alternate plank colors
            color = palette.WOOD_BROWN if (angle // 15) % 2 == 0 else palette.WOOD_DARK
            b.put(x, y, z, color)
            
    # 2. Iron Hoops (at bottom, top, and middle)
    for z in [3, height-4, height//2]:
        for angle in range(0, 360, 1):
            rad = math.radians(angle)
            # Match the bulge at this Z
            bulge = math.sin((z / height) * 3.14159) * 1.5
            r = radius + bulge + 0.5 # Slightly wider than planks
            x = int(round(math.cos(rad) * r))
            y = int(round(math.sin(rad) * r))
            b.put(x, y, z, palette.STONE_DARK)
            
    # Top Cap
    for r_fill in range(int(radius)):
        for angle in range(360):
            rad = math.radians(angle)
            x = int(round(math.cos(rad) * r_fill))
            y = int(round(math.sin(rad) * r_fill))
            b.put(x, y, 0, palette.WOOD_DARK)
            b.put(x, y, height-1, palette.WOOD_DARK)
            
    return b

def make_window(width=24, height=32):
    """Returns a window with a wood cross and a bottom shelf."""
    b = VoxelBuilder()
    hw = width // 2
    hh = height // 2
    
    # 1. Glowing Glass (Back plane)
    b.fill(-hw+2, 0, 2, hw-2, 0, height-2, palette.WINDOW_GLOW)
    
    # 2. Ghost Bloom Aura (1v in front of glass)
    b.fill(-hw+1, 1, 1, hw-1, 1, height-1, palette.GHOST_WHITE)
    
    # 3. Outer Frame (Now at Y=1-2)
    b.fill(-hw, 1, 0, hw, 2, 1, palette.WOOD_DARK) # Bottom rail
    b.fill(-hw, 1, height-1, hw, 2, height, palette.WOOD_DARK) # Top rail
    b.fill(-hw, 1, 0, -hw+1, 2, height, palette.WOOD_DARK) # Left
    b.fill(hw-1, 1, 0, hw, 2, height, palette.WOOD_DARK) # Right
    
    # 4. The Wood Cross (Mullions at Y=2)
    b.fill(-hw, 2, hh-1, hw, 2, hh+1, palette.WOOD_DARK) # Horizontal
    b.fill(-1, 2, 0, 1, 2, height, palette.WOOD_DARK) # Vertical
    
    # 5. The Bottom Shelf (Protruding Y+)
    b.fill(-hw-2, 1, 0, hw+2, 5, 2, palette.WOOD_BROWN)
    
    return b

def make_bar_counter(width=48):
    """Returns a detailed wooden bar counter with overhang and corbels."""
    b = VoxelBuilder()
    hw = width // 2
    # 1. Main Base (Slightly narrower than top)
    b.fill(-hw, 0, 0, hw, 6, 35, palette.WOOD_DARK)
    
    # 2. Recessed Foot Rail (Carved from front bottom)
    b.carve(-hw, 0, 0, hw, 2, 4)
    b.fill(-hw, 1, 1, hw, 2, 2, palette.STONE_DARK) # Iron foot rail
    
    # 3. Countertop (Deep overhang on customer side Y+)
    # Overhangs 8v forward, 2v on sides
    b.fill(-hw-2, 0, 35, hw+2, 14, 38, palette.WOOD_BROWN)
    
    # 4. Corbels (Support brackets under overhang)
    for x in [-hw+4, -hw//2, 0, hw//2, hw-4]:
        # Vertical support rib
        b.fill(x-1, 6, 25, x+1, 10, 35, palette.WOOD_DARK)
        # Diagonal-ish brace
        b.fill(x-1, 10, 30, x+1, 12, 35, palette.WOOD_DARK)
        
    # 5. Decorative molding on the front panel
    b.fill(-hw, 6, 10, hw, 7, 12, palette.WOOD_LIGHT)
    b.fill(-hw, 6, 25, hw, 7, 27, palette.WOOD_LIGHT)
    
    return b

def make_bottle(color=None):
    """Returns a small glass bottle."""
    b = VoxelBuilder()
    c = color if color else palette.WINDOW_GLOW
    # Bottle Body
    b.fill(-1, -1, 0, 1, 1, 4, c)
    # Neck
    b.fill(0, 0, 5, 0, 0, 6, palette.WOOD_DARK)
    # Cork
    b.put(0, 0, 7, palette.WOOD_BROWN)
    return b

def make_barstool():
    """Returns a tall wooden barstool."""
    b = VoxelBuilder()
    # 4 Tall Legs
    for x, y in [(-4, -4), (4, -4), (-4, 4), (4, 4)]:
        b.fill(x, y, 0, x+1, y+1, 22, palette.WOOD_DARK)
    # Footrest rails
    b.fill(-4, -4, 6, 4, -3, 7, palette.WOOD_BROWN)
    b.fill(-4, 4, 6, 4, 5, 7, palette.WOOD_BROWN)
    # Round Seat
    for r in range(6):
        for a in range(360):
            rad = math.radians(a)
            sx = int(round(math.cos(rad) * r))
            sy = int(round(math.sin(rad) * r))
            b.put(sx, sy, 22, palette.WOOD_BROWN)
            b.put(sx, sy, 23, palette.WOOD_LIGHT)
    return b

def make_mug():
    """Returns a simple wooden mug."""
    b = VoxelBuilder()
    # Body (5x5x6)
    b.fill(-2, -2, 0, 2, 2, 5, palette.WOOD_BROWN)
    # Interior (hollowed top)
    b.carve(-1, -1, 1, 1, 1, 5)
    # Handle
    b.fill(2, 0, 1, 3, 0, 4, palette.WOOD_DARK)
    return b

def make_tankard():
    """Returns a larger metal-bound tankard."""
    b = VoxelBuilder()
    # Body (7x7x9)
    b.fill(-3, -3, 0, 3, 3, 8, palette.WOOD_DARK)
    # Iron Hoops
    for z in [1, 6]:
        for a in range(0, 360, 10):
            rad = math.radians(a)
            x = int(round(math.cos(rad) * 3.2))
            y = int(round(math.sin(rad) * 3.2))
            b.put(x, y, z, palette.STONE_DARK)
    # Froth (White top)
    b.fill(-2, -2, 8, 2, 2, 8, palette.WHITE)
    # Handle
    b.fill(3, 0, 2, 5, 0, 6, palette.STONE_DARK)
    return b

def make_stairs(width=40, height=80, steps=20):
    """Returns a set of wooden stairs."""
    b = VoxelBuilder()
    step_h = height // steps
    step_d = 8 # depth of each tread
    for i in range(steps):
        # Each step is a box
        b.fill(-width//2, i*step_d, i*step_h, width//2, (i+1)*step_d, i*step_h + step_h, palette.WOOD_BROWN)
        # Side supports (stringers)
        b.fill(-width//2, i*step_d, 0, -width//2+2, (i+1)*step_d, i*step_h, palette.WOOD_DARK)
        b.fill(width//2-2, i*step_d, 0, width//2, (i+1)*step_d, i*step_h, palette.WOOD_DARK)
    return b

def make_door(width=30, height=50):
    """Returns a heavy iron-bound tavern door."""
    b = VoxelBuilder()
    hw = width // 2
    # Wood planks
    b.fill(-hw, 0, 0, hw, 2, height, palette.WOOD_BROWN)
    # Iron bands (top, middle, bottom)
    for z in [5, height//2, height-10]:
        b.fill(-hw-1, -1, z, hw+1, 3, z+2, palette.STONE_DARK)
    # Iron Studs
    for x in [-hw+4, 0, hw-4]:
        for z in [5, height//2, height-10]:
            b.put(x, -1, z+1, palette.STONE_HIGHLIGHT)
    # Handle (Ring)
    b.fill(hw-8, -2, 22, hw-6, -1, 26, palette.STONE_HIGHLIGHT)
    return b

def make_shelf(width=60, tiers=3):
    """Returns a wall-mounted shelving unit."""
    b = VoxelBuilder()
    hw = width // 2
    for i in range(tiers):
        z = i * 25
        # Shelf plank
        b.fill(-hw, 0, z, hw, 10, z+2, palette.WOOD_BROWN)
        # Supports
        b.fill(-hw+5, 0, z-5, -hw+7, 2, z, palette.WOOD_DARK)
        b.fill(hw-7, 0, z-5, hw-5, 2, z, palette.WOOD_DARK)
    return b

def make_chain_link():
    """Returns a single small iron chain link."""
    b = VoxelBuilder()
    # A small 3x4 vertical ring
    b.fill(-1, 0, 0, 1, 0, 3, palette.STONE_DARK)
    b.carve(0, 0, 1, 0, 0, 2)
    return b

def make_hoop(radius=6, color=None):
    """Returns a horizontal iron or wood hoop."""
    b = VoxelBuilder()
    c = color if color else palette.STONE_DARK
    for angle in range(0, 360, 5):
        rad = angle * (3.14159 / 180.0)
        x = int(round(math.cos(rad) * radius))
        y = int(round(math.sin(rad) * radius))
        b.put(x, y, 0, c)
    return b