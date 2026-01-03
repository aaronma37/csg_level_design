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

# --- CHARACTER RANGE (100-149) ---
set_color(100, 47, 30, 16)
set_color(101, 174, 141, 98)
set_color(102, 1, 1, 1)
set_color(103, 237, 213, 188)
set_color(104, 107, 84, 53)
set_color(105, 38, 59, 128)
set_color(106, 189, 67, 51)
set_color(107, 61, 47, 82)
set_color(108, 172, 173, 166)
set_color(109, 97, 62, 28)
set_color(110, 79, 121, 117)
set_color(111, 115, 163, 158)
set_color(112, 236, 188, 126)
set_color(113, 56, 97, 169)
set_color(114, 133, 94, 52)
set_color(115, 118, 2, 1)
set_color(116, 125, 116, 97)
set_color(117, 24, 236, 218)
set_color(118, 45, 41, 55)
set_color(119, 182, 130, 53)
set_color(120, 140, 33, 32)
set_color(121, 225, 191, 90)
set_color(122, 79, 71, 52)
set_color(123, 94, 11, 146)
set_color(124, 212, 179, 141)
set_color(125, 248, 250, 239)
set_color(126, 105, 39, 97)
set_color(127, 61, 47, 30)
set_color(128, 200, 34, 23)
set_color(129, 136, 200, 218)
set_color(130, 159, 122, 85)
set_color(131, 29, 32, 31)
set_color(132, 91, 19, 16)
set_color(133, 207, 163, 71)
set_color(134, 221, 224, 220)
set_color(135, 16, 163, 200)
set_color(136, 146, 94, 27)
set_color(137, 157, 149, 132)
set_color(138, 239, 116, 6)
set_color(139, 55, 60, 61)
set_color(140, 242, 217, 163)
set_color(141, 195, 159, 120)
set_color(142, 37, 51, 71)
set_color(143, 195, 197, 187)
set_color(144, 60, 21, 66)
set_color(145, 97, 94, 93)
set_color(146, 27, 27, 45)
set_color(147, 169, 12, 214)
set_color(148, 127, 79, 201)
set_color(149, 48, 52, 43)

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