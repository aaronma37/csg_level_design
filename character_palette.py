# Minimal 12-Color Palette for Character
PALETTE_COLORS = [(0, 0, 0, 0)] * 256

def set_color(idx, r, g, b, a=255):
    PALETTE_COLORS[idx] = (r, g, b, a)

# 1. Hair / Deep Shadows
set_color(1, 20, 20, 20)     # Black/Charcoal

# 2. Clothes (Green)
set_color(2, 60, 100, 60)    # Base Green
set_color(3, 40, 70, 40)     # Shadow Green

# 3. Skin
set_color(4, 255, 210, 170)  # Peach Skin
set_color(5, 200, 160, 130)  # Tan/Shadow Skin

# 4. Leather / Boots
set_color(6, 140, 90, 60)    # Brown
set_color(7, 90, 60, 40)     # Dark Brown

# 5. Telescope / Metal
set_color(8, 220, 180, 80)   # Brass/Gold
set_color(9, 120, 120, 130)  # Steel/Grey

# 6. Highlights
set_color(10, 255, 255, 255) # White (Eyes/Reflections)
set_color(11, 240, 240, 230) # Off-White

# 7. Magic
set_color(12, 160, 50, 255)  # Purple

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
