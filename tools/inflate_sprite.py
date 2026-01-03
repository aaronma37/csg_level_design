import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import struct
import sys
import math
import os
from PIL import Image

# --- 1. ROBUST VOX WRITER (Based on csg_compiler.py) ---
class CustomVoxelModel:
    def __init__(self, voxels, palette_list):
        self.voxels = voxels # List of (x,y,z, color_idx)
        self.palette = palette_list # List of (r,g,b,a) tuples

    def _pack_string(self, s):
        b = s.encode('utf-8')
        return struct.pack('<I', len(b)) + b

    def _pack_dict(self, d):
        content = struct.pack('<I', len(d))
        for k, v in d.items():
            content += self._pack_string(str(k))
            content += self._pack_string(str(v))
        return content

    def _make_chunk(self, tag, content):
        return tag + struct.pack('<II', len(content), 0) + content

    def save(self, filename):
        print(f"Saving {len(self.voxels)} voxels to {filename}...")
        
        # 1. Bounds
        xs = [v[0] for v in self.voxels]
        ys = [v[1] for v in self.voxels]
        zs = [v[2] for v in self.voxels]
        
        if not xs: return
        min_x, min_y, min_z = min(xs), min(ys), min(zs)
        mx, my, mz = max(xs)-min_x+1, max(ys)-min_y+1, max(zs)-min_z+1
        
        # 2. Normalize Data
        normalized_vox = []
        for v in self.voxels:
            normalized_vox.append((v[0]-min_x, v[1]-min_y, v[2]-min_z, v[3]))

        chunks = b''
        
        # 3. SIZE & XYZI (The Model)
        chunks += self._make_chunk(b'SIZE', struct.pack('<III', mx, my, mz))
        
        xyzi_content = struct.pack('<I', len(normalized_vox))
        for v in normalized_vox:
            chunks += struct.pack('<BBBB', v[0], v[1], v[2], v[3])
        chunks += self._make_chunk(b'XYZI', xyzi_content)
        
        # 4. RGBA (Custom Palette)
        pal_bytes = bytearray(1024)
        for i in range(256):
            # VOX palette is 1-based. Entry 0 in file is Color 1.
            # Entry 255 in file is Color 256.
            # My palette_list is 0-based.
            if i < len(self.palette):
                c = self.palette[i]
                # MagicaVoxel expects RGBA
                pal_bytes[i*4] = c[0]
                pal_bytes[i*4+1] = c[1]
                pal_bytes[i*4+2] = c[2]
                pal_bytes[i*4+3] = c[3] 
        chunks += self._make_chunk(b'RGBA', pal_bytes)

        # 5. SCENE GRAPH (Required for some viewers)
        # Root -> Shape -> Model 0
        
        # Transform (Root)
        center_x, center_y, center_z = mx//2, my//2, mz//2
        
        root_content = struct.pack('<I', 0) # ID 0
        root_content += self._pack_dict({}) 
        root_content += struct.pack('<I', 1) # 1 Child
        root_content += struct.pack('<i', -1) # Reserved
        root_content += struct.pack('<i', 0) # Layer 0
        root_content += struct.pack('<I', 1) # 1 Frame
        root_content += self._pack_dict({"_t": f"0 0 0"}) # Translation
        chunks += self._make_chunk(b'nTRN', root_content)
        
        # Shape (Node 1)
        shape_content = struct.pack('<I', 1) # ID 1
        shape_content += self._pack_dict({})
        shape_content += struct.pack('<I', 1) # 1 Model
        shape_content += struct.pack('<I', 0) # Model ID 0
        shape_content += self._pack_dict({})
        chunks += self._make_chunk(b'nSHP', shape_content)
        
        # 6. LAYR (Optional but good)
        layr_content = struct.pack('<I', 0)
        layr_content += self._pack_dict({"_name": "Base"})
        layr_content += struct.pack('<i', -1)
        chunks += self._make_chunk(b'LAYR', layr_content)

        # 7. MAIN
        with open(filename, 'wb') as f:
            f.write(b'VOX ' + struct.pack('<I', 150))
            f.write(b'MAIN' + struct.pack('<II', 0, len(chunks)) + chunks)

# --- 2. INFLATION LOGIC ---
def get_distance_to_edge(alpha_map, w, h, x, y):
    if alpha_map[y][x] == 0: return 0
    min_dist = 10 # Cap search
    
    start_x = max(0, x - 10)
    end_x = min(w, x + 11)
    start_y = max(0, y - 10)
    end_y = min(h, y + 11)
    
    found = False
    for dy in range(start_y, end_y):
        for dx in range(start_x, end_x):
            if alpha_map[dy][dx] == 0:
                d = math.sqrt((x-dx)**2 + (y-dy)**2)
                if d < min_dist:
                    min_dist = d
                    found = True
    return min_dist

def generate_inflated_vox(image_path, output_path):
    print(f"Inflating {image_path}...")
    img = Image.open(image_path).convert("RGBA")
    
    # Resize to safe bounds
    w, h = img.size
    if h > 80:
        ratio = 80 / h
        w = int(w * ratio)
        h = 80
        img = img.resize((w, h), Image.Resampling.NEAREST)
    
    pixels = img.load()
    
    # Analyze Colors & Transparency
    alpha_map = [[0]*w for _ in range(h)]
    palette_list = []
    color_map = {} # (r,g,b,a) -> index (1-based)
    
    # Transparent at Index 0 (implicit, not in palette_list usually)
    # But for RGBA chunk, Entry 0 is Index 1.
    
    for y in range(h):
        for x in range(w):
            r,g,b,a = pixels[x,y]
            if a > 100:
                alpha_map[y][x] = 1
                c = (r,g,b,255)
                if c not in color_map:
                    if len(palette_list) < 255:
                        palette_list.append(c)
                        color_map[c] = len(palette_list) # 1-based index: Entry 0 is Index 1
            else:
                alpha_map[y][x] = 0
                
    # Generate Voxels
    voxels = []
    MAX_THICK = 6
    
    for y in range(h):
        for x in range(w):
            if alpha_map[y][x]:
                dist = get_distance_to_edge(alpha_map, w, h, x, y)
                thickness = min(MAX_THICK, max(1, int(dist * 1.5)))
                
                r,g,b,a = pixels[x,y]
                c_idx = color_map.get((r,g,b,255), 1)
                
                # Z-Up
                wz = h - 1 - y
                wx = x
                
                # Center Y (Depth) around 0
                start_y = -(thickness // 2)
                for dy in range(thickness):
                    wy = start_y + dy + 10 # Offset to be positive
                    voxels.append((wx, wy, wz, c_idx))
                    
    model = CustomVoxelModel(voxels, palette_list)
    model.save(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python inflate_sprite.py <input> <output>")
    else:
        generate_inflated_vox(sys.argv[1], sys.argv[2])