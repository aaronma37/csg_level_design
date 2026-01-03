# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CRITICAL: SEMANTIC COLOR PALETTE
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# The ORDER and EXISTENCE of these colors are essential for game stability.
# Many systems (including character texture lookups and shader materials) 
# depend on specific indices.
# 
# DO NOT REMOVE colors or CHANGE their indices without explicit permission.
# Doing so will break voxel reconstructions and in-game rendering.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# 0-20: Wood textures
# 21-40: Stone textures
# 41-99: Misc / General
# 100-149: Character Range (PROTECTED: Used for Voxel Character Reconstructions)
# 240-249: Standard Emissive (Visible)
# 250-255: Ghost Emissive (Alpha 0, high bloom)

PALETTE_COLORS = [(0, 0, 0, 255)] * 256

def set_color(idx, r, g, b, a=255):
    PALETTE_COLORS[idx] = (r, g, b, a)

# --- WOOD RANGE (0-20) ---
set_color(1, 100, 70, 40)    # Wood Brown
set_color(2, 60, 40, 20)     # Wood Dark
set_color(3, 140, 100, 60)   # Wood Light
set_color(4, 80, 50, 30)     # Wood Grain A
set_color(5, 110, 80, 50)    # Wood Grain B

# --- STONE RANGE (21-40) ---
set_color(21, 150, 150, 150) # Stone Light
set_color(22, 100, 100, 100) # Stone Dark
set_color(23, 180, 180, 180) # Stone Highlight
set_color(24, 130, 120, 110) # Stone Warm
set_color(25, 80, 80, 90)    # Stone Cold

# --- MISC / FABRIC (41-99) ---
set_color(41, 120, 20, 20)   # Fabric Red (Deep)
set_color(42, 20, 50, 100)   # Fabric Blue (Navy)
set_color(43, 180, 150, 50)  # Fabric Gold (Thread)
set_color(44, 235, 225, 200) # Beige Light
set_color(45, 230, 220, 195) # Beige Medium
set_color(46, 225, 215, 190) # Beige Dark
set_color(47, 40, 40, 40)    # Charcoal
set_color(48, 80, 20, 20)    # Fabric Maroon
set_color(49, 150, 130, 100) # Fabric Burlap (Brown)
set_color(50, 255, 255, 255) # Pure White

# --- CHARACTER RANGE (100-149) ---
# WARNING: DO NOT MODIFY OR REMOVE THESE COLORS. 
set_color(100, 47, 30, 16); set_color(101, 174, 141, 98); set_color(102, 1, 1, 1); set_color(103, 237, 213, 188)
set_color(104, 107, 84, 53); set_color(105, 38, 59, 128); set_color(106, 189, 67, 51); set_color(107, 61, 47, 82)
set_color(108, 172, 173, 166); set_color(109, 97, 62, 28); set_color(110, 79, 121, 117); set_color(111, 115, 163, 158)
set_color(112, 236, 188, 126); set_color(113, 56, 97, 169); set_color(114, 133, 94, 52); set_color(115, 118, 2, 1)
set_color(116, 125, 116, 97); set_color(117, 24, 236, 218); set_color(118, 45, 41, 55); set_color(119, 182, 130, 53)
set_color(120, 140, 33, 32); set_color(121, 225, 191, 90); set_color(122, 79, 71, 52); set_color(123, 94, 11, 146)
set_color(124, 212, 179, 141); set_color(125, 248, 250, 239); set_color(126, 105, 39, 97); set_color(127, 61, 47, 30)
set_color(128, 200, 34, 23); set_color(129, 136, 200, 218); set_color(130, 159, 122, 85); set_color(131, 29, 32, 31)
set_color(132, 91, 19, 16); set_color(133, 207, 163, 71); set_color(134, 221, 224, 220); set_color(135, 16, 163, 200)
set_color(136, 146, 94, 27); set_color(137, 157, 149, 132); set_color(138, 239, 116, 6); set_color(139, 55, 60, 61)
set_color(140, 242, 217, 163); set_color(141, 195, 159, 120); set_color(142, 37, 51, 71); set_color(143, 195, 197, 187)
set_color(144, 60, 21, 66); set_color(145, 97, 94, 93); set_color(146, 27, 27, 45); set_color(147, 169, 12, 214)
set_color(148, 127, 79, 201); set_color(149, 48, 52, 43)

# --- STANDARD EMISSIVE (240-249) ---
set_color(240, 255, 100, 0)   # Fire Orange
set_color(241, 255, 200, 0)   # Fire Yellow
set_color(242, 160, 32, 240)  # Electric Purple (Visible)
set_color(243, 230, 245, 255) # Window Glow (Bright White-Blue)

# --- GHOST EMISSIVE (250-255) ---
for i in range(250, 256):
    set_color(i, 150, 200, 255, 0)
set_color(250, 200, 50, 255, 0) # Ghost Purple
set_color(251, 50, 255, 50, 0)  # Ghost Green
set_color(252, 255, 255, 255, 0) # Ghost White

# Constants
WOOD_BROWN = 1; WOOD_DARK = 2; WOOD_LIGHT = 3
STONE_BASE = 21; STONE_DARK = 22; STONE_LIGHT = 23
STONE_HIGHLIGHT = 23
FABRIC_RED = 41; FABRIC_BLUE = 42; FABRIC_GOLD = 43; FABRIC_MAROON = 48; FABRIC_BURLAP = 49
BEIGE_LIGHT = 44; BEIGE_MEDIUM = 45; BEIGE_DARK = 46
WHITE = 50
PURPLE_GLOW = 242; WINDOW_GLOW = 243
GHOST_PURPLE = 250; GHOST_WHITE = 252
GHOST_GREEN = 251; FIRE_CORE = 240; FIRE_GLOW = 241

def get_palette_bytes():
    import struct
    content = b''
    for i in range(1, 256):
        r, g, b, a = PALETTE_COLORS[i]
        content += struct.pack('<BBBB', r, g, b, a)
    r, g, b, a = PALETTE_COLORS[0]
    content += struct.pack('<BBBB', r, g, b, a)
    return content
