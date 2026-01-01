# Shared Color Palette
# Format: Index: (R, G, B, A)

PALETTE_COLORS = [
    (0, 0, 0, 0),          # 0: Empty
    (100, 70, 40, 255),    # 1: Brown (Floor/Generic Wood)
    (220, 200, 160, 255),  # 2: Sandstone (Light)
    (60, 40, 20, 255),     # 3: Dark Wood (Beams/Furniture)
    (180, 140, 90, 255),   # 4: Light Wood (Planks)
    (200, 50, 50, 255),    # 5: Red (Fire/Carpet)
    (240, 230, 200, 255),  # 6: Beige (Light)
    (230, 215, 180, 255),  # 7: Beige (Medium)
    (210, 190, 150, 255),  # 8: Beige (Dark)
    (140, 120, 90, 255),   # 9: Sandstone (Darker)
    (255, 100, 0, 255),    # 10: Orange (Fire Core)
]

# Named Constants for Scripts
EMPTY = 0
WOOD_BROWN = 1
STONE_LIGHT = 2
WOOD_DARK = 3
WOOD_LIGHT = 4
RED = 5
BEIGE_LIGHT = 6
BEIGE_MEDIUM = 7
BEIGE_DARK = 8
STONE_DARKER = 9
FIRE_ORANGE = 10
STONE_DARK = 2 # Reuse Stone light/dark if needed, or define more. 
# Wait, I shifted indices. Let's be careful.
# Original: 2=StoneLight, 7=StoneDark, 8=StoneDarker, 9=FireOrange
# Let's re-align to be safe.

PALETTE_COLORS = [
    (0, 0, 0, 0),          # 0: Empty
    (100, 70, 40, 255),    # 1: Brown
    (170, 170, 170, 255),  # 2: Castle Stone (Light)
    (60, 40, 20, 255),     # 3: Dark Wood
    (180, 140, 90, 255),   # 4: Light Wood
    (200, 50, 50, 255),    # 5: Red
    (235, 225, 200, 255),  # 6: Beige (Light) - More subtle
    (230, 220, 195, 255),  # 7: Beige (Medium)
    (225, 215, 190, 255),  # 8: Beige (Dark)
    (130, 130, 130, 255),  # 9: Castle Stone (Dark)
    (100, 100, 100, 255),  # 10: Castle Stone (Darker)
    (255, 100, 0, 255),    # 11: Orange (Fire Core)
]

# Constants
EMPTY = 0
WOOD_BROWN = 1
STONE_LIGHT = 2
WOOD_DARK = 3
WOOD_LIGHT = 4
RED = 5
BEIGE_LIGHT = 6
BEIGE_MEDIUM = 7
BEIGE_DARK = 8
STONE_DARK = 9
STONE_DARKER = 10
FIRE_ORANGE = 11

def get_palette_bytes():
    """Returns the 255-color palette as bytes for VOX format"""
    import struct
    content = b''
    for i in range(1, 256):
        if i < len(PALETTE_COLORS):
            r, g, b, a = PALETTE_COLORS[i]
            content += struct.pack('<BBBB', r, g, b, a)
        else:
            # Fill rest with default grey
            content += struct.pack('<BBBB', 150, 150, 150, 255)
    return content
