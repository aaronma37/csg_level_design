import struct
import json
import sys
import os
import palette

class VoxWriter:
    def __init__(self):
        self.palette = palette.PALETTE_COLORS
        self.models = [] # list of (size, voxels)

    def add_model(self, voxels):
        if not voxels:
            self.models.append(((1,1,1), []))
            return len(self.models) - 1
        xs, ys, zs = zip(*[(v[0], v[1], v[2]) for v in voxels])
        min_x, min_y, min_z = min(xs), min(ys), min(zs)
        mx, my, mz = max(xs)-min_x+1, max(ys)-min_y+1, max(zs)-min_z+1
        norm_voxels = [(v[0]-min_x, v[1]-min_y, v[2]-min_z, v[3]) for v in voxels]
        self.models.append(((mx, my, mz), norm_voxels))
        return len(self.models) - 1

    def _pack_str(self, s):
        b = s.encode('utf-8')
        return struct.pack('<I', len(b)) + b

    def _pack_dict(self, d):
        content = struct.pack('<I', len(d))
        for k, v in d.items():
            content += self._pack_str(str(k))
            content += self._pack_str(str(v))
        return content

    def _make_chunk(self, tag, content):
        return tag + struct.pack('<II', len(content), 0) + content

    def save(self, filename, scene_instances):
        """scene_instances: list of (model_index, pos, rot, name)"""
        chunks = b''
        
        # 1. Models (Must come before Scene Graph)
        chunks += self._make_chunk(b'PACK', struct.pack('<I', len(self.models)))
        for size, voxels in self.models:
            chunks += self._make_chunk(b'SIZE', struct.pack('<III', *size))
            xyzi_payload = struct.pack('<I', len(voxels))
            for v in voxels: xyzi_payload += struct.pack('<BBBB', *v)
            chunks += self._make_chunk(b'XYZI', xyzi_payload)

        # 2. Scene Graph
        # STRICT ORDER: Root TRN (0), then Group (1), then others.
        graph_chunks = []
        instance_trn_ids = []
        next_id = 2

        # PRE-GENERATE Instances to know their IDs
        instance_chunks = b''
        for model_idx, pos, rot, name in scene_instances:
            m_size, _ = self.models[model_idx]
            tx, ty, tz = pos[0] + m_size[0]//2, pos[1] + m_size[1]//2, pos[2] + m_size[2]//2
            
            shp_id = next_id; next_id += 1
            trn_id = next_id; next_id += 1
            instance_trn_ids.append(trn_id)
            
            # nSHP
            shp_payload = struct.pack('<I', shp_id) + self._pack_dict({})
            shp_payload += struct.pack('<I', 1) + struct.pack('<I', model_idx) + self._pack_dict({})
            instance_chunks += self._make_chunk(b'nSHP', shp_payload)
            
            # Rotation around Z axis in MagicaVoxel
            # Spec: bits 0-1 (col0 idx), 2-3 (col1 idx), 4 (col0 sign), 5 (col1 sign), 6 (col2 sign)
            # 0: 4, 90: 33, 180: 52, 270: 17
            r_byte = {0: 4, 90: 33, 180: 52, 270: 17}.get(rot, 4)
            trn_payload = struct.pack('<I', trn_id) + self._pack_dict({"_name": name})
            trn_payload += struct.pack('<I', shp_id) + struct.pack('<i', -1) + struct.pack('<i', 0)
            trn_payload += struct.pack('<I', 1) + self._pack_dict({"_t": f"{tx} {ty} {tz}", "_r": str(r_byte)})
            instance_chunks += self._make_chunk(b'nTRN', trn_payload)

        # Root nTRN (ID 0)
        root_payload = struct.pack('<I', 0) + self._pack_dict({"_name": "root"})
        root_payload += struct.pack('<I', 1) + struct.pack('<i', -1) + struct.pack('<i', 0)
        root_payload += struct.pack('<I', 1) + self._pack_dict({})
        chunks += self._make_chunk(b'nTRN', root_payload)

        # Main Group (ID 1)
        grp_payload = struct.pack('<I', 1) + self._pack_dict({})
        grp_payload += struct.pack('<I', len(instance_trn_ids))
        for tid in instance_trn_ids: grp_payload += struct.pack('<I', tid)
        chunks += self._make_chunk(b'nGRP', grp_payload)
        
        # Add instances
        chunks += instance_chunks

        # 3. Metadata chunks
        chunks += self._make_chunk(b'LAYR', struct.pack('<I', 0) + self._pack_dict({"_name": "Base"}) + struct.pack('<i', -1))
        
        pal_bytes = bytearray(1024)
        for i in range(1, 256):
            c = self.palette[i] if i < len(self.palette) else (150,150,150,255)
            for j in range(4): pal_bytes[(i-1)*4 + j] = c[j]
        chunks += self._make_chunk(b'RGBA', pal_bytes)

        for i in range(1, 256):
            chunks += self._make_chunk(b'MATL', struct.pack('<I', i) + self._pack_dict({"_type": "_diffuse"}))

        # Write File
        with open(filename, 'wb') as f:
            f.write(b'VOX ' + struct.pack('<I', 150))
            f.write(b'MAIN' + struct.pack('<II', 0, len(chunks)) + chunks)

def load_vox_voxels(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []
    try:
        with open(filename, 'rb') as f:
            if f.read(4) != b'VOX ': return []
            f.read(4) # version
            if f.read(4) != b'MAIN': return []
            f.read(8) # main sizes
            
            # Read subchunks of MAIN
            while True:
                cid = f.read(4)
                if not cid: break
                cs, chs = struct.unpack('<II', f.read(8))
                if cid == b'XYZI':
                    nv = struct.unpack('<I', f.read(4))[0]
                    voxels = []
                    for _ in range(nv):
                        voxels.append(struct.unpack('<BBBB', f.read(4)))
                    return voxels
                else:
                    f.read(cs + chs)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return []

def run_composer(layout_file, output_file="final_scene.vox"):
    print(f"Composing Scene from {layout_file}...")
    with open(layout_file, 'r') as f:
        scene_data = json.load(f)
    
    writer = VoxWriter()
    loaded_models = {}
    scene_instances = []
    
    for item in scene_data:
        aid = item['asset_id']
        pos = item['pos']
        rot = item.get('rot', 0)
        
        if aid not in loaded_models:
            vox_file = f"{aid}.vox"
            voxels = load_vox_voxels(vox_file)
            print(f"  Loading {vox_file}: {len(voxels)} voxels")
            loaded_models[aid] = writer.add_model(voxels)
        
        scene_instances.append((loaded_models[aid], pos, rot, aid))
    
    writer.save(output_file, scene_instances)
    print(f"Done! Scene saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python scene_composer.py layout.json")
    else: run_composer(sys.argv[1])
