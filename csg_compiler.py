import struct
import json
import sys
import os
import palette # Import shared palette

# --- 1. THE VOX WRITER (With CSG Logic) ---
class VoxelModel:
    def __init__(self):
        # Sparse storage: Key=(x,y,z), Value=ColorIndex
        self.voxels = {}
        # Use shared palette
        self.palette = palette.PALETTE_COLORS

    def add_cuboid(self, x, y, z, dx, dy, dz, color):
        """Standard 'Union' Operation"""
        for i in range(dx):
            for j in range(dy):
                for k in range(dz):
                    self.voxels[(x+i, y+j, z+k)] = color

    def subtract_cuboid(self, x, y, z, dx, dy, dz):
        """Standard 'Difference' Operation (The Crack Maker)"""
        for i in range(dx):
            for j in range(dy):
                for k in range(dz):
                    coord = (x+i, y+j, z+k)
                    if coord in self.voxels:
                        del self.voxels[coord]

    def intersect_cuboid(self, x, y, z, dx, dy, dz):
        """Standard 'Intersection' (Keep only what overlaps)"""
        to_keep = {}
        for i in range(dx):
            for j in range(dy):
                for k in range(dz):
                    coord = (x+i, y+j, z+k)
                    if coord in self.voxels:
                        to_keep[coord] = self.voxels[coord]
        self.voxels = to_keep

    def save(self, filename):
        if not self.voxels:
            print(f"Warning: Model {filename} is empty.")
            return

        print(f"Saving {len(self.voxels)} voxels to {filename}...")
        
        # 1. Prepare Data
        # MagicaVoxel expects XYZI data
        vox_data = []
        for (x,y,z), color in self.voxels.items():
            vox_data.append((x, y, z, color))
            
        # 2. Calculate Bounds
        xs, ys, zs = zip(*[(v[0], v[1], v[2]) for v in vox_data])
        min_x, min_y, min_z = min(xs), min(ys), min(zs)
        mx, my, mz = max(xs)-min_x+1, max(ys)-min_y+1, max(zs)-min_z+1
        
        # 3. Write Binary
        with open(filename, 'wb') as f:
            # Header
            f.write(b'VOX ' + struct.pack('<I', 150))
            
            # Main Chunk Container
            children = b''
            
            # SIZE Chunk
            children += self._make_chunk(b'SIZE', struct.pack('<III', mx, my, mz))
            
            # XYZI Chunk (Voxel Data)
            # Normalize coordinates
            normalized_vox_data = []
            for v in vox_data:
                normalized_vox_data.append((v[0]-min_x, v[1]-min_y, v[2]-min_z, v[3]))
            
            xyzi_content = struct.pack('<I', len(normalized_vox_data))
            for v in normalized_vox_data:
                # x, y, z, color_index
                xyzi_content += struct.pack('<BBBB', v[0], v[1], v[2], v[3])
            children += self._make_chunk(b'XYZI', xyzi_content)
            
            # RGBA Chunk (Palette)
            pal_content = b''
            # Write our defined colors first
            for i in range(1, 256):
                if i < len(self.palette):
                    r,g,b,a = self.palette[i]
                    pal_content += struct.pack('<BBBB', r, g, b, a)
                else:
                    # Fill rest with default grey
                    pal_content += struct.pack('<BBBB', 150, 150, 150, 255)
            children += self._make_chunk(b'RGBA', pal_content)
            
            # Write Main Chunk
            f.write(b'MAIN' + struct.pack('<II', 0, len(children)) + children)

    def _make_chunk(self, tag, content):
        return tag + struct.pack('<II', len(content), 0) + content

# --- 2. THE COMPILER (Interpreter) ---
def compile_asset(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    model = VoxelModel()
    asset_name = data.get("name", "unknown")
    
    print(f"Compiling Asset: {asset_name}...")
    
    # Execute Instructions in Order
    for op in data.get("instructions", []):
        action = op.get("op")
        x, y, z = op.get("pos", [0,0,0])
        dx, dy, dz = op.get("size", [1,1,1])
        color = op.get("color", 1)
        
        if action == "add":
            model.add_cuboid(x, y, z, dx, dy, dz, color)
        elif action == "subtract":
            model.subtract_cuboid(x, y, z, dx, dy, dz)
        elif action == "intersect":
            model.intersect_cuboid(x, y, z, dx, dy, dz)
            
    # Output Filename
    output_filename = f"{asset_name}.vox"
    model.save(output_filename)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csg_compiler.py asset_definition.json")
    else:
        compile_asset(sys.argv[1])
