import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import struct
import os

class VoxReader:
    def __init__(self, filename):
        self.filename = filename
        self.voxels = [] # List of (x, y, z, color_index)
        self.palette = [] # List of (r, g, b, a) tuples
        self.size = (0, 0, 0)
        self.read()

    def read(self):
        with open(self.filename, 'rb') as f:
            # 1. Header
            header = f.read(4)
            version = struct.unpack('<I', f.read(4))[0]
            
            if header != b'VOX ':
                raise ValueError("Not a valid VOX file")

            # 2. Chunks
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                
                content_size = struct.unpack('<I', f.read(4))[0]
                children_size = struct.unpack('<I', f.read(4))[0]
                
                content = f.read(content_size)
                
                if chunk_id == b'SIZE':
                    self.size = struct.unpack('<III', content)
                
                elif chunk_id == b'XYZI':
                    num_voxels = struct.unpack('<I', content[:4])[0]
                    for i in range(num_voxels):
                        x, y, z, c = struct.unpack('<BBBB', content[4+i*4:8+i*4])
                        self.voxels.append((x, y, z, c))
                
                elif chunk_id == b'RGBA':
                    num_colors = len(content) // 4
                    for i in range(num_colors):
                        # Indices 1-255 (0 is empty usually, but palette stores 256 colors)
                        r, g, b, a = struct.unpack('<BBBB', content[i*4:i*4+4])
                        self.palette.append((r, g, b, a))
                
                # Skip children (MAIN chunk has children, but we just read through them effectively if flat, 
                # but standard VOX is hierarchical. 
                # csg_compiler writes flat structure inside MAIN: SIZE, XYZI, RGBA sequentially.
                # But standard reader might need to recurse if MAIN has children bytes not part of content.
                # Wait, csg_compiler writes: 
                # MAIN + content_size=0 + children_size=len(children) + children
                # So MAIN's content is empty, everything is in children.
                # My reader loop above reads 'MAIN', sees content_size=0, children_size=BIG.
                # Then it reads 0 bytes of content.
                # Then it continues to read... wait.
                # If MAIN has children, those children follow immediately.
                # My loop just reads chunks sequentially. 
                # If MAIN is the first chunk, it consumes its header.
                # Then we need to ensure we read the sub-chunks.
                # If I just loop, I will read the next chunk ID.
                # Since MAIN content is 0, the next bytes ARE the start of the first child chunk.
                # So a simple linear loop works for this specific structure!
                
                pass

    def get_voxel_data(self):
        return self.voxels, self.size, self.palette
