import struct
import numpy as np
import json
import os
import sys
import palette

def generate_palette_png(filename="palette_texture.png"):
    """Generates a 256x1 PNG from the palette.py colors using pure Python + zlib."""
    import zlib
    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 256, 1, 8, 2, 0, 0, 0)
    def make_chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    raw_data = b'\x00'
    for i in range(256):
        r, g, b, a = palette.PALETTE_COLORS[i]
        raw_data += struct.pack('BBB', r, g, b)
    idat = make_chunk(b'IDAT', zlib.compress(raw_data))
    iend = make_chunk(b'IEND', b'')
    with open(filename, 'wb') as f:
        f.write(signature + ihdr + idat + iend)
    print(f"Generated {filename}")

class VoxToGltf:
    def __init__(self, vox_path):
        self.vox_path = vox_path
        self.models = [] 
        self.nodes = {}
        self.world_voxels = {}
        self.bounds_min = [1e9, 1e9, 1e9]
        self.bounds_max = [-1e9, -1e9, -1e9]
        self.load_vox()
        self.recompose_world()

    def _read_dict(self, f):
        num_pairs = struct.unpack('<I', f.read(4))[0]
        d = {}
        for _ in range(num_pairs):
            kl = struct.unpack('<I', f.read(4))[0]
            k = f.read(kl).decode('utf-8')
            vl = struct.unpack('<I', f.read(4))[0]
            v = f.read(vl).decode('utf-8')
            d[k] = v
        return d

    def load_vox(self):
        self.palette = []
        with open(self.vox_path, 'rb') as f:
            if f.read(4) != b'VOX ': raise ValueError("Not a VOX file")
            f.read(4) # version
            while True:
                cid = f.read(4)
                if not cid: break
                cs, chs = struct.unpack('<II', f.read(8))
                print(f"DEBUG: Found chunk {cid} cs={cs} chs={chs}")
                if cid == b'MAIN': continue
                
                start_p = f.tell()
                if cid == b'SIZE':
                    dims = struct.unpack('<III', f.read(12))
                    print(f"DEBUG: SIZE {dims}")
                    self.models.append({"dims": dims, "voxels": {}})
                elif cid == b'XYZI':
                    n = struct.unpack('<I', f.read(4))[0]
                    print(f"DEBUG: XYZI {n} voxels")
                    for _ in range(n):
                        x, y, z, c = struct.unpack('<BBBB', f.read(4))
                        self.models[-1]["voxels"][(x, y, z)] = c
                elif cid == b'RGBA':
                    for _ in range(256):
                        r, g, b, a = struct.unpack('<BBBB', f.read(4))
                        self.palette.append((r, g, b, a))
                elif cid == b'nTRN':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attr = self._read_dict(f)
                    child = struct.unpack('<I', f.read(4))[0]
                    f.read(12)
                    frame_attr = self._read_dict(f)
                    self.nodes[nid] = {"type": "TRN", "child": child, "t": frame_attr.get("_t", "0 0 0"), "r": frame_attr.get("_r", "4")}
                    print(f"DEBUG: nTRN {nid} -> {child}")
                elif cid == b'nGRP':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attr = self._read_dict(f)
                    num_children = struct.unpack('<I', f.read(4))[0]
                    children = [struct.unpack('<I', f.read(4))[0] for _ in range(num_children)]
                    self.nodes[nid] = {"type": "GRP", "children": children}
                    print(f"DEBUG: nGRP {nid} kids={children}")
                elif cid == b'nSHP':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attr = self._read_dict(f)
                    f.read(4)
                    mid = struct.unpack('<I', f.read(4))[0]
                    self.nodes[nid] = {"type": "SHP", "model": mid}
                    print(f"DEBUG: nSHP {nid} model={mid}")
                f.seek(start_p + cs)

    def write_palette_png(self, filename):
        import zlib
        pal = self.palette if self.palette and len(self.palette) == 256 else palette.PALETTE_COLORS
        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 256, 1, 8, 2, 0, 0, 0)
        def make_chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        ihdr = make_chunk(b'IHDR', ihdr_data)
        raw_data = b'\x00'
        for i in range(256):
            r, g, b, a = pal[i]
            raw_data += struct.pack('BBB', r, g, b)
        idat = make_chunk(b'IDAT', zlib.compress(raw_data))
        iend = make_chunk(b'IEND', b'')
        with open(filename, 'wb') as f:
            f.write(signature + ihdr + idat + iend)
        print(f"Generated {filename}")

    def recompose_world(self):
        print(f"Recomposing {len(self.models)} models into world space...")
        
        # MagicaVoxel rotation lookup (24 possible orientations)
        def apply_rot(lx, ly, lz, mx, my, mz, r_byte):
            # 1. Center coordinates
            cx, cy, cz = lx - mx//2, ly - my//2, lz - mz//2
            
            # 2. Extract rotation components from byte
            # Bits 0-1: Index of row 0
            # Bits 2-3: Index of row 1
            # Bits 4, 5, 6: Signs of row 0, 1, 2
            r0_idx = r_byte & 3
            r1_idx = (r_byte >> 2) & 3
            # Third row index is implied
            r2_idx = 3 - r0_idx - r1_idx
            
            s0 = -1 if (r_byte >> 4) & 1 else 1
            s1 = -1 if (r_byte >> 5) & 1 else 1
            s2 = -1 if (r_byte >> 6) & 1 else 1
            
            coords = [cx, cy, cz]
            nx = coords[r0_idx] * s0
            ny = coords[r1_idx] * s1
            nz = coords[r2_idx] * s2
            
            return nx, ny, nz

        def traverse(nid, current_t, current_r):
            node = self.nodes.get(nid)
            if not node: return
            if node["type"] == "TRN":
                t_parts = [int(x) for x in node["t"].split()]
                # MagicaVoxel rotations don't stack simple additions, 
                # but for our simple tavern layout they are top-level.
                # However, we'll just track the latest rotation for the child SHP.
                r_byte = int(node.get("r", "4"))
                new_t = (current_t[0]+t_parts[0], current_t[1]+t_parts[1], current_t[2]+t_parts[2])
                traverse(node["child"], new_t, r_byte)
            elif node["type"] == "GRP":
                for cnid in node["children"]: traverse(cnid, current_t, current_r)
            elif node["type"] == "SHP":
                model = self.models[node["model"]]
                mx, my, mz = model["dims"]
                for (lx, ly, lz), c in model["voxels"].items():
                    # Apply rotation around local center
                    nx, ny, nz = apply_rot(lx, ly, lz, mx, my, mz, current_r)
                    
                    # Apply world translation (current_t is already the center pos in MV)
                    wx, wy, wz = int(nx + current_t[0]), int(ny + current_t[1]), int(nz + current_t[2])
                    
                    self.world_voxels[(wx, wy, wz)] = c
                    self.bounds_min = [min(self.bounds_min[0], wx), min(self.bounds_min[1], wy), min(self.bounds_min[2], wz)]
                    self.bounds_max = [max(self.bounds_max[0], wx), max(self.bounds_max[1], wy), max(self.bounds_max[2], wz)]

        if 0 in self.nodes: traverse(0, (0,0,0), 4)
        elif self.models:
            m = self.models[0]
            self.world_voxels = m["voxels"]
            self.bounds_max, self.bounds_min = list(m["dims"]), [0,0,0]
        print(f"Total world voxels: {len(self.world_voxels)}")

    def get_voxel(self, x, y, z):
        return self.world_voxels.get((x, y, z), 0)

    def mesh(self):
        groups = {"standard": {"verts": [], "norms": [], "uvs": [], "indices": []},
                  "emissive": {"verts": [], "norms": [], "uvs": [], "indices": []}}
        bmin, bmax = self.bounds_min, self.bounds_max
        for d in range(6):
            if d < 2:   k_idx, i_idx, j_idx = 0, 1, 2
            elif d < 4: k_idx, i_idx, j_idx = 1, 0, 2
            else:       k_idx, i_idx, j_idx = 2, 0, 1
            backface = (d % 2 == 1)
            norm = [0,0,0]; norm[k_idx] = (1 if not backface else -1)
            for k in range(int(bmin[k_idx]), int(bmax[k_idx]) + 1):
                mask = {}
                for coord_key in self.world_voxels:
                    if coord_key[k_idx] == k:
                        neighbor = list(coord_key)
                        neighbor[k_idx] += (1 if not backface else -1)
                        if self.get_voxel(*neighbor) == 0:
                            mask[(coord_key[i_idx], coord_key[j_idx])] = self.world_voxels[coord_key]
                if not mask: continue
                visited = set()
                sorted_keys = sorted(mask.keys())
                for i, j in sorted_keys:
                    color = mask[(i, j)]
                    if (i, j) not in visited:
                        w, h = 1, 1
                        while mask.get((i, j + w)) == color and (i, j + w) not in visited: w += 1
                        while True:
                            row_ok = True
                            for cur_j in range(j, j + w):
                                if mask.get((i + h, cur_j)) != color or (i + h, cur_j) in visited:
                                    row_ok = False; break
                            if not row_ok: break
                            h += 1
                        # Group 240-255 as emissive (includes visible and ghost ranges)
                        g = groups["emissive" if color >= 240 else "standard"]
                        v_start = len(g["verts"])
                        uv_x = (color + 0.5) / 256.0
                        for di, dj in [(0,0), (0,1), (1,1), (1,0)]:
                            pt = [0,0,0]
                            pt[k_idx], pt[i_idx], pt[j_idx] = k + (1 if not backface else 0), i + di * h, j + dj * w
                            # Swapping Y and Z for GLTF (Y-up)
                            gltf_pt = [float(pt[0]), float(pt[2]), float(pt[1])]
                            gltf_norm = [float(norm[0]), float(norm[2]), float(norm[1])]
                            g["verts"].append(gltf_pt); g["norms"].append(gltf_norm); g["uvs"].append([uv_x, 0.5])
                        if backface: g["indices"].extend([v_start, v_start+1, v_start+2, v_start, v_start+2, v_start+3])
                        else: g["indices"].extend([v_start, v_start+2, v_start+1, v_start, v_start+3, v_start+2])
                        for hi in range(h):
                            for wj in range(w): visited.add((i + hi, j + wj))
        return groups

    def export(self, out_path):
        groups = self.mesh()
        buffer_data = bytearray()
        def add_to_buffer(data, fmt):
            nonlocal buffer_data
            offset = len(buffer_data); packed = b''
            for row in data: packed += struct.pack(fmt, *row) if isinstance(row, list) else struct.pack(fmt, row)
            buffer_data += packed
            return offset, len(packed)
        bin_name = os.path.basename(out_path).replace(".gltf", ".bin")
        gltf = {
            "asset": {"version": "2.0"}, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}], "meshes": [{"primitives": []}],
            "materials": [{"name": "Standard", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 0.8}},
                          {"name": "Emissive", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 0.8}, "emissiveTexture": {"index": 0}, "emissiveFactor": [1.0, 1.0, 1.0]}],
            "textures": [{"source": 0}], "images": [{"uri": "palette_texture.png"}], "samplers": [{"magFilter": 9728, "minFilter": 9728}],
            "bufferViews": [], "accessors": [], "buffers": [{"byteLength": 0, "uri": bin_name}]
        }
        for name in ["standard", "emissive"]:
            g = groups[name]
            if not g["indices"]: continue
            pos_off, pos_len = add_to_buffer(g["verts"], "<fff")
            pos_acc = len(gltf["accessors"])
            gltf["accessors"].append({"bufferView": len(gltf["bufferViews"]), "componentType": 5126, "count": len(g["verts"]), "type": "VEC3", "max": np.max(g["verts"], axis=0).tolist(), "min": np.min(g["verts"], axis=0).tolist()})
            gltf["bufferViews"].append({"buffer": 0, "byteOffset": pos_off, "byteLength": pos_len, "target": 34962})
            norm_off, norm_len = add_to_buffer(g["norms"], "<fff")
            norm_acc = len(gltf["accessors"])
            gltf["accessors"].append({"bufferView": len(gltf["bufferViews"]), "componentType": 5126, "count": len(g["norms"]), "type": "VEC3"})
            gltf["bufferViews"].append({"buffer": 0, "byteOffset": norm_off, "byteLength": norm_len, "target": 34962})
            uv_off, uv_len = add_to_buffer(g["uvs"], "<ff")
            uv_acc = len(gltf["accessors"])
            gltf["accessors"].append({"bufferView": len(gltf["bufferViews"]), "componentType": 5126, "count": len(g["uvs"]), "type": "VEC2"})
            gltf["bufferViews"].append({"buffer": 0, "byteOffset": uv_off, "byteLength": uv_len, "target": 34962})
            ind_off, ind_len = add_to_buffer(g["indices"], "<I")
            ind_acc = len(gltf["accessors"])
            gltf["accessors"].append({"bufferView": len(gltf["bufferViews"]), "componentType": 5125, "count": len(g["indices"]), "type": "SCALAR"})
            gltf["bufferViews"].append({"buffer": 0, "byteOffset": ind_off, "byteLength": ind_len, "target": 34963})
            gltf["meshes"][0]["primitives"].append({"attributes": {"POSITION": pos_acc, "NORMAL": norm_acc, "TEXCOORD_0": uv_acc}, "indices": ind_acc, "material": 0 if name == "standard" else 1})
        gltf["buffers"][0]["byteLength"] = len(buffer_data)
        with open(out_path, 'w') as f: json.dump(gltf, f, indent=2)
        with open(os.path.join(os.path.dirname(out_path), bin_name), 'wb') as f: f.write(buffer_data)
        print(f"Exported {out_path} and {bin_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python vox_to_gltf.py <input.vox> [output.gltf]"); sys.exit(1)
    input_vox, output_gltf = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1].replace(".vox", ".gltf")
    
    # Determine output directory
    output_dir = os.path.dirname(output_gltf)
    palette_path = os.path.join(output_dir, "palette_texture.png") if output_dir else "palette_texture.png"
    
    # Always generate to stay in sync with palette.py
    generate_palette_png(palette_path)
    VoxToGltf(input_vox).export(output_gltf)