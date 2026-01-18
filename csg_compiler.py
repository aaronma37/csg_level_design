import struct
import json
import sys
import os
import palette # Import shared palette
from primitives import volumes

# --- 1. THE VOX WRITER (With CSG Logic) ---
class VoxelModel:
    def __init__(self, custom_palette=None):
        # Sparse storage: Key=(x,y,z), Value=ColorIndex
        self.voxels = {}
        # Use shared palette or custom one
        self.palette = custom_palette if custom_palette else palette.PALETTE_COLORS

    def apply_operation(self, op_type, coords, color=1):
        if op_type == "add":
            for c in coords:
                self.voxels[c] = color
        elif op_type == "subtract":
            for c in coords:
                if c in self.voxels:
                    del self.voxels[c]
        elif op_type == "intersect":
            to_keep = {}
            coord_set = set(coords)
            for c in self.voxels:
                if c in coord_set:
                    to_keep[c] = self.voxels[c]
            self.voxels = to_keep

    def add_cuboid(self, x, y, z, dx, dy, dz, color):
        coords = volumes.get_cuboid_voxels(x, y, z, dx, dy, dz)
        self.apply_operation("add", coords, color)

    def subtract_cuboid(self, x, y, z, dx, dy, dz):
        coords = volumes.get_cuboid_voxels(x, y, z, dx, dy, dz)
        self.apply_operation("subtract", coords)

    def intersect_cuboid(self, x, y, z, dx, dy, dz):
        coords = volumes.get_cuboid_voxels(x, y, z, dx, dy, dz)
        self.apply_operation("intersect", coords)

    def _pack_string(self, s):
        b = s.encode('utf-8')
        return struct.pack('<I', len(b)) + b

    def _pack_dict(self, d):
        content = struct.pack('<I', len(d))
        for k, v in d.items():
            content += self._pack_string(str(k))
            content += self._pack_string(str(v))
        return content

    def save(self, filename):
        if not self.voxels:
            print(f"Warning: Model {filename} is empty.")
            return

        print(f"Saving {len(self.voxels)} voxels to {filename}...")
        
        # 1. Prepare Data
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
            
            # Chunks Container
            chunks = b''
            
            # PACK Chunk
            chunks += self._make_chunk(b'PACK', struct.pack('<I', 1))
            
            # SIZE Chunk
            chunks += self._make_chunk(b'SIZE', struct.pack('<III', mx, my, mz))
            
            # XYZI Chunk (Voxel Data)
            normalized_vox_data = []
            for v in vox_data:
                normalized_vox_data.append((v[0]-min_x, v[1]-min_y, v[2]-min_z, v[3]))
            
            xyzi_content = struct.pack('<I', len(normalized_vox_data))
            for v in normalized_vox_data:
                xyzi_content += struct.pack('<BBBB', v[0], v[1], v[2], v[3])
            chunks += self._make_chunk(b'XYZI', xyzi_content)
            
            # RGBA Chunk (Palette)
            pal_bytes = bytearray(1024)
            for i in range(1, 256):
                c = self.palette[i] if i < len(self.palette) else (150, 150, 150, 255)
                pal_bytes[(i-1)*4 : i*4] = struct.pack('<BBBB', *c)
            chunks += self._make_chunk(b'RGBA', pal_bytes)
            
            # LAYR Chunk
            layr_content = struct.pack('<I', 0) # Layer ID
            layr_content += self._pack_dict({"_name": "Base"}) # Attributes
            layr_content += struct.pack('<i', -1) # Reserved
            chunks += self._make_chunk(b'LAYR', layr_content)

            # SCENE GRAPH CHUNKS (nTRN, nSHP)
            # Root Node (0) -> Shape Node (1) -> Model (0)
            tx = min_x + (mx // 2)
            ty = min_y + (my // 2)
            tz = min_z + (mz // 2)
            
            # Root nTRN
            root_payload = struct.pack('<I', 0)
            root_payload += self._pack_dict({"_name": os.path.basename(filename)})
            root_payload += struct.pack('<I', 1) # Child is Shape node
            root_payload += struct.pack('<i', -1)
            root_payload += struct.pack('<i', 0)
            root_payload += struct.pack('<I', 1)
            root_payload += self._pack_dict({"_t": f"{tx} {ty} {tz}"})
            chunks += self._make_chunk(b'nTRN', root_payload)
            
            # Shape nSHP
            shp_content = struct.pack('<I', 1)
            shp_content += self._pack_dict({})
            shp_content += struct.pack('<I', 1)
            shp_content += struct.pack('<I', 0) # Model 0
            shp_content += self._pack_dict({})
            chunks += self._make_chunk(b'nSHP', shp_content)
            
            # MATL Chunks (Indices 1 to 255)
            for i in range(1, 256):
                matl_payload = struct.pack('<I', i)
                matl_payload += self._pack_dict({"_type": "_diffuse"})
                chunks += self._make_chunk(b'MATL', matl_payload)
            
            # Write Main Chunk
            f.write(b'MAIN' + struct.pack('<II', 0, len(chunks)) + chunks)

    def _make_chunk(self, tag, content):
        return tag + struct.pack('<II', len(content), 0) + content

# --- 2. THE COMPILER (Interpreter) ---
def compile_asset(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        # Handle list-based format where metadata is missing
        instructions = data
        asset_name = os.path.basename(json_path).replace(".json", "")
        custom_pal = None
    else:
        instructions = data.get("instructions", [])
        asset_name = data.get("name", "unknown")
        custom_pal = data.get("palette")

    model = VoxelModel(custom_palette=custom_pal)
    print(f"Compiling Asset: {asset_name}...")
    
    # Execute Instructions in Order
    for op in instructions:
        action = op.get("op") # e.g., "add", "subtract", "intersect"
        shape = op.get("shape", "cuboid")
        pos = op.get("pos", [0,0,0])
        color = op.get("color", 1)
        
        coords = []
        if shape == "cuboid":
            size = op.get("size", [1,1,1])
            coords = volumes.get_cuboid_voxels(pos[0], pos[1], pos[2], size[0], size[1], size[2])
        elif shape == "sphere":
            radius = op.get("radius", 1)
            coords = volumes.get_sphere_voxels(pos[0], pos[1], pos[2], radius)
        elif shape == "cylinder":
            radius = op.get("radius", 1)
            height = op.get("height", 1)
            axis = op.get("axis", "z")
            coords = volumes.get_cylinder_voxels(pos[0], pos[1], pos[2], radius, height, axis)
        elif shape == "cone":
            radius_bottom = op.get("radius_bottom", 1)
            radius_top = op.get("radius_top", 0)
            height = op.get("height", 1)
            axis = op.get("axis", "z")
            coords = volumes.get_cone_voxels(pos[0], pos[1], pos[2], radius_bottom, radius_top, height, axis)
        elif shape == "ellipsoid":
            size = op.get("size", [1,1,1]) # Treated as radii [rx, ry, rz]
            coords = volumes.get_ellipsoid_voxels(pos[0], pos[1], pos[2], size[0], size[1], size[2])
        elif shape == "point_cloud":
            points = op.get("points", [])
            # points are relative to pos
            coords = [(p[0] + pos[0], p[1] + pos[1], p[2] + pos[2]) for p in points]
            
        # Legacy Support for "op": "add", "subtract", "intersect" as separate actions
        # if "shape" is not provided but "op" is one of the old actions.
        if action in ["add", "subtract", "intersect"]:
            # If shape was "cuboid" by default, we use it.
            # size might have been in the old format.
            if shape == "cuboid" and not coords:
                 size = op.get("size", [1,1,1])
                 coords = volumes.get_cuboid_voxels(pos[0], pos[1], pos[2], size[0], size[1], size[2])
            model.apply_operation(action, coords, color)
            
    # Output Filename
    output_filename = f"{asset_name}.vox"
    if os.path.exists("vox") and os.path.isdir("vox"):
        output_filename = os.path.join("vox", output_filename)
    model.save(output_filename)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csg_compiler.py asset_definition.json")
    else:
        compile_asset(sys.argv[1])
