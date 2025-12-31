# Shared Color Palette
# Format: Index: (R, G, B, A)

PALETTE_COLORS = [
    (0, 0, 0, 0),          # 0: Empty
    (100, 70, 40, 255),    # 1: Brown (Floor/Generic Wood)
    (150, 150, 150, 255),  # 2: Stone Grey (Light)
    (60, 40, 20, 255),     # 3: Dark Wood (Beams/Furniture)
    (180, 140, 90, 255),   # 4: Light Wood (Planks)
    (200, 50, 50, 255),    # 5: Red (Fire/Carpet)
    (220, 220, 220, 255),  # 6: White (Plaster)
    (120, 120, 120, 255),  # 7: Stone Grey (Dark) - NEW
    (80, 80, 80, 255),     # 8: Stone Grey (Darker) - NEW
    (255, 100, 0, 255),    # 9: Orange (Fire Core) - NEW
]

# Named Constants for Scripts
EMPTY = 0
WOOD_BROWN = 1
STONE_LIGHT = 2
WOOD_DARK = 3
WOOD_LIGHT = 4
RED = 5
WHITE = 6
STONE_DARK = 7
STONE_DARKER = 8
FIRE_ORANGE = 9

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
