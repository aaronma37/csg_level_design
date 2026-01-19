import struct
import numpy as np
import json
import os
import sys
import palette

def generate_palette_png(filename="palette_texture.png"):
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
    def __init__(self, vox_path, no_center=False):
        self.vox_path = vox_path
        self.no_center = no_center
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
                chunk_id = f.read(4)
                if not chunk_id: break
                chunk_len, child_len = struct.unpack('<II', f.read(8))
                if chunk_id == b'SIZE':
                    w, d, h = struct.unpack('<III', f.read(12))
                    self.models.append({"size": (w, d, h), "voxels": {}})
                elif chunk_id == b'XYZI':
                    num_voxels = struct.unpack('<I', f.read(4))[0]
                    for _ in range(num_voxels):
                        x, y, z, c = struct.unpack('<BBBB', f.read(4))
                        self.models[-1]["voxels"][(x, y, z)] = c
                elif chunk_id == b'nTRN':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attrs = self._read_dict(f)
                    cid, rid, lid, num_frames = struct.unpack('<IIII', f.read(16))
                    frames = [self._read_dict(f) for _ in range(num_frames)]
                    self.nodes[nid] = {"type": "TRN", "child": cid, "t": frames[0].get("_t", "0 0 0"), "r": frames[0].get("_r", "4")}
                elif chunk_id == b'nGRP':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attrs = self._read_dict(f)
                    num_children = struct.unpack('<I', f.read(4))[0]
                    children = [struct.unpack('<I', f.read(4))[0] for _ in range(num_children)]
                    self.nodes[nid] = {"type": "GRP", "children": children}
                elif chunk_id == b'nSHP':
                    nid = struct.unpack('<I', f.read(4))[0]
                    attrs = self._read_dict(f)
                    num_models = struct.unpack('<I', f.read(4))[0]
                    ms = []
                    for _ in range(num_models):
                        mid = struct.unpack('<I', f.read(4))[0]
                        mattrs = self._read_dict(f)
                        ms.append(mid)
                    self.nodes[nid] = {"type": "SHP", "model": ms[0]}
                else: f.read(chunk_len)

    def recompose_world(self):
        def apply_rot_raw(x, y, z, r):
            # Magical MagicaVoxel rotation byte handling
            row0 = [(r >> 0) & 3, (r >> 4) & 1]
            row1 = [(r >> 2) & 3, (r >> 5) & 1]
            row2 = [3 - row0[0] - row1[0], (r >> 6) & 1]
            coords = [x, y, z]
            r0_idx, s0 = row0[0], (1 if row0[1] == 0 else -1)
            r1_idx, s1 = row1[0], (1 if row1[1] == 0 else -1)
            r2_idx, s2 = row2[0], (1 if row2[1] == 0 else -1)
            return coords[r0_idx] * s0, coords[r1_idx] * s1, coords[r2_idx] * s2

        raw_voxels = {}
        def traverse(nid, current_t, current_r):
            node = self.nodes.get(nid)
            if not node: return
            if node["type"] == "TRN":
                t_parts = [int(x) for x in node["t"].split()]
                r_byte = int(node.get("r", "4"))
                new_t = (current_t[0]+t_parts[0], current_t[1]+t_parts[1], current_t[2]+t_parts[2])
                traverse(node["child"], new_t, r_byte)
            elif node["type"] == "GRP":
                for cnid in node["children"]: traverse(cnid, current_t, current_r)
            elif node["type"] == "SHP":
                model = self.models[node["model"]]
                for (lx, ly, lz), c in model["voxels"].items():
                    nx, ny, nz = apply_rot_raw(lx, ly, lz, current_r)
                    wx, wy, wz = int(nx + current_t[0]), int(ny + current_t[1]), int(nz + current_t[2])
                    raw_voxels[(wx, wy, wz)] = c

        if 0 in self.nodes: traverse(0, (0,0,0), 4)
        elif self.models: raw_voxels = self.models[0]["voxels"]

        if not raw_voxels: return

        # 2. Second Pass: Calculate bounds and apply centering/grounding
        pts = np.array(list(raw_voxels.keys()))
        rmin = pts.min(axis=0)
        rmax = pts.max(axis=0)
        
        if self.no_center:
            center_x = 0
            center_y = 0
            ground_z = rmin[2] # Still ground Z to 0
        else:
            center_x = (rmin[0] + rmax[0]) // 2
            center_y = (rmin[1] + rmax[1]) // 2
            ground_z = rmin[2]

        for (wx, wy, wz), c in raw_voxels.items():
            nx, ny, nz = wx - center_x, wy - center_y, wz - ground_z
            self.world_voxels[(nx, ny, nz)] = c
            self.bounds_min = [min(self.bounds_min[0], nx), min(self.bounds_min[1], ny), min(self.bounds_min[2], nz)]
            self.bounds_max = [max(self.bounds_max[0], nx), max(self.bounds_max[1], ny), max(self.bounds_max[2], nz)]

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
        print(f"Exported {out_path}")

if __name__ == "__main__":
    args = sys.argv[1:]
    no_center = False
    if "--no-center" in args:
        no_center = True
        args.remove("--no-center")
    
    if len(args) < 1:
        print("Usage: python vox_to_gltf.py [--no-center] input.vox [output.gltf]")
        sys.exit(1)

    input_vox = args[0]
    output_gltf = args[1] if len(args) > 1 else input_vox.replace(".vox", ".gltf")

    generate_palette_png()
    VoxToGltf(input_vox, no_center=no_center).export(output_gltf)