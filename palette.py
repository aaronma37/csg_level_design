# Semantic Color Palette
# 0-20: Wood textures
# 21-40: Stone textures
# 41-239: Misc / General
# 240-255: Emissive / Glowing

PALETTE_COLORS = [(0, 0, 0, 0)] * 256

def set_color(idx, r, g, b, a=255):
    PALETTE_COLORS[idx] = (r, g, b, a)

# --- WOOD RANGE (0-20) ---
set_color(1, 100, 70, 40)    # Wood Brown (Base)
set_color(2, 60, 40, 20)     # Wood Dark (Bark/Beams)
set_color(3, 140, 100, 60)   # Wood Light (Planks)
set_color(4, 80, 50, 30)     # Wood Grain A
set_color(5, 110, 80, 50)    # Wood Grain B

# --- STONE RANGE (21-40) ---
set_color(21, 150, 150, 150) # Stone Light (Base)
set_color(22, 100, 100, 100) # Stone Dark (Shadows)
set_color(23, 180, 180, 180) # Stone Highlight
set_color(24, 130, 120, 110) # Stone Warm (Sandy)
set_color(25, 80, 80, 90)    # Stone Cold (Slate)

# --- MISC (41-239) ---
set_color(41, 200, 50, 50)   # Generic Red
set_color(42, 50, 150, 50)   # Generic Green
set_color(43, 50, 50, 200)   # Generic Blue
set_color(44, 235, 225, 200) # Beige Light
set_color(45, 230, 220, 195) # Beige Medium
set_color(46, 225, 215, 190) # Beige Dark
set_color(47, 40, 40, 40)    # Charcoal (Robes)
set_color(48, 100, 20, 20)   # Deep Red (Sash)
set_color(49, 80, 0, 100)    # Dark Purple (Book)
set_color(251, 160, 32, 240) # Electric Purple (Magic)
set_color(252, 255, 50, 255) # Bright Magenta (Magic)

# --- EMISSIVE RANGE (240-255) ---
set_color(240, 255, 100, 0)   # Fire Orange (Core)
set_color(241, 255, 200, 0)   # Fire Yellow
set_color(242, 200, 50, 0)    # Fire Red-Orange
set_color(250, 100, 200, 255) # Magic Glow (Blue)

# Named Constants
WOOD_BASE = 1
WOOD_DARK = 2
WOOD_LIGHT = 3
WOOD_BROWN = 1 # Re-alias for floor
STONE_BASE = 21
STONE_DARK = 22
STONE_LIGHT = 23
STONE_DARKER = 22 # Re-alias
BEIGE_LIGHT = 44
BEIGE_MEDIUM = 45
BEIGE_DARK = 46
RED = 41
FIRE_CORE = 240
FIRE_GLOW = 241
FIRE_ORANGE = 240

def get_palette_bytes():
    import struct
    content = b''
    # MagicaVoxel palette chunk is exactly 1024 bytes (256 colors)
    # The first entry in the chunk is Color 1, and so on. Color 0 is at the end.
    for i in range(1, 256):
        r, g, b, a = PALETTE_COLORS[i]
        content += struct.pack('<BBBB', r, g, b, a)
    # Last color in chunk
    r, g, b, a = PALETTE_COLORS[0]
    content += struct.pack('<BBBB', r, g, b, a)
    return content