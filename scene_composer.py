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
            
            # Handle rotation-swapped dimensions for center calculation
            # 0 and 180: dimensions stay the same. 90 and 270: swap X and Y.
            cur_w, cur_d = m_size[0], m_size[1]
            if rot == 90 or rot == 270:
                cur_w, cur_d = m_size[1], m_size[0]
                
            tx, ty, tz = pos[0] + cur_w // 2, pos[1] + cur_d // 2, pos[2] + m_size[2] // 2
            
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

import math

def rotate_point(x, y, angle_deg):
    """Rotates a 2D point around (0,0)."""
    if angle_deg == 0: return x, y
    rad = math.radians(angle_deg)
    # Standard rotation matrix
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    # MagicaVoxel/Menori coordinate systems might need specific checks, 
    # but standard math is:
    # x' = x cos - y sin
    # y' = x sin + y cos
    # NOTE: Check if we need to invert for coordinate system (Y-down vs Y-up)
    # Assuming standard Euclidean for now.
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    return new_x, new_y

def load_layout_recursively(layout_path, parent_pos=(0,0,0), parent_rot=0):
    if not os.path.exists(layout_path):
        print(f"Warning: Layout file not found: {layout_path}")
        return []

    with open(layout_path, 'r') as f:
        data = json.load(f)
    
    flat_items = []
    local_instances = {} # id -> { pos, rot, asset_id } (Local to this layout, but parent-transform applied?? No, let's store local-to-parent to be safe, or just resolved global?)
    # Easier to store RESOLVED GLOBAL coords in local_instances for easy math, 
    # BUT we need to be careful about the hierarchy. 
    # Let's store RESOLVED GLOBAL.
    
    for item in data:
        aid = item['asset_id']
        
        # 1. Determine Local Transform (lx, ly, lz, lr)
        if 'snap_to' in item:
            # Resolution Logic
            target_id, point_name = item['snap_to'].split('.')
            if target_id not in local_instances:
                print(f"Error: Snap target '{target_id}' not found (must be defined before use).")
                continue
            
            t_info = local_instances[target_id]
            t_aid = t_info['asset_id']
            t_pos = t_info['pos'] # Global
            t_rot = t_info['rot'] # Global
            
            # Load target asset to get snap points
            # Search in csg/ or same dir
            # We assume t_aid is a leaf asset for now, or a collection that has snap_points at top level?
            # Usually assets have snap_points.
            t_path = os.path.join(os.path.dirname(layout_path), f"{t_aid}.json")
            if not os.path.exists(t_path): t_path = os.path.join("csg", f"{t_aid}.json")
            
            snap_def = None
            if os.path.exists(t_path):
                try:
                    with open(t_path, 'r') as tf:
                        t_data = json.load(tf)
                        if 'snap_points' in t_data:
                            snap_def = t_data['snap_points'].get(point_name)
                except: pass
            
            if not snap_def:
                print(f"Error: Snap point '{point_name}' not found on asset '{t_aid}'.")
                continue
                
            # Apply Snap Point Transform
            # The snap point (sx, sy, sz, sr) is local to the target asset (which is at t_pos, t_rot)
            sx, sy, sz = snap_def['pos']
            sr = snap_def.get('rot', 0)
            
            # Rotate snap point by target's global rotation
            rsx, rsy = rotate_point(sx, sy, t_rot)
            
            # New Global Pos = Target Global + Rotated Snap Offset
            gx = t_pos[0] + rsx
            gy = t_pos[1] + rsy
            gz = t_pos[2] + sz
            gr = (t_rot + sr) % 360
            
        else:
            # Standard explicit transform
            lx, ly, lz = item.get('pos', [0,0,0])
            lr = item.get('rot', 0)
            
            # Apply parent rotation to local position
            rx, ry = rotate_point(lx, ly, parent_rot)
            
            gx = parent_pos[0] + rx
            gy = parent_pos[1] + ry
            gz = parent_pos[2] + lz
            gr = (lr + parent_rot) % 360

        # 2. Store if ID is present
        if 'id' in item:
            local_instances[item['id']] = {
                'pos': (gx, gy, gz),
                'rot': gr,
                'asset_id': aid
            }

        # 3. Process Asset (Leaf or Collection)
        collection_path = os.path.join(os.path.dirname(layout_path), f"{aid}.json")
        if not os.path.exists(collection_path):
            collection_path = os.path.join("csg", f"{aid}.json")
        
        is_collection = False
        if os.path.exists(collection_path):
            try:
                with open(collection_path, 'r') as cf:
                    c_data = json.load(cf)
                if isinstance(c_data, list) and len(c_data) > 0 and isinstance(c_data[0], dict) and 'asset_id' in c_data[0]:
                    is_collection = True
            except:
                pass

        if is_collection:
            flat_items.extend(load_layout_recursively(collection_path, (gx, gy, gz), gr))
        else:
            flat_items.append({
                'asset_id': aid,
                'pos': [int(gx), int(gy), int(gz)],
                'rot': int(gr)
            })
            
    return flat_items

def run_composer(layout_file, output_file=None, merge=False):
    print(f"Composing Scene from {layout_file}...")
    
    # Use recursive loader instead of direct json.load
    scene_data = load_layout_recursively(layout_file)
    
    # Generate Lua version of the layout
    base_name = os.path.basename(layout_file).replace(".json", "")
    scenes_dir = os.path.join("csg_assets", "scenes")
    lua_output = os.path.join(scenes_dir, f"{base_name}.lua")
    
    lua_lines = ["-- Layout generated procedurally.", "return {"]
    for item in scene_data:
        aid = item['asset_id']
        pos = item['pos']
        rot = item.get('rot', 0)
        lua_lines.append(f"    {{ asset_id = '{aid}', pos = {{{pos[0]}, {pos[1]}, {pos[2]}}}, rot = {rot} }},")
    lua_lines.append("}")
    
    os.makedirs(scenes_dir, exist_ok=True)
    with open(lua_output, 'w') as f:
        f.write("\n".join(lua_lines) + "\n")
    print(f"  Lua layout saved to {lua_output}")

    if merge:
        if output_file is None:
            output_file = f"{base_name}.vox"
            if os.path.exists("vox") and os.path.isdir("vox"):
                output_file = os.path.join("vox", output_file)
        
        writer = VoxWriter()
        loaded_models = {}
        scene_instances = []
        
        for item in scene_data:
            aid = item['asset_id']
            pos = item['pos']
            rot = item.get('rot', 0)
            
            if aid not in loaded_models:
                vox_file = f"{aid}.vox"
                if not os.path.exists(vox_file) and os.path.exists(os.path.join("vox", vox_file)):
                    vox_file = os.path.join("vox", vox_file)
                
                voxels = load_vox_voxels(vox_file)
                print(f"  Loading {vox_file}: {len(voxels)} voxels")
                loaded_models[aid] = writer.add_model(voxels)
            
            scene_instances.append((loaded_models[aid], pos, rot, aid))
        
        writer.save(output_file, scene_instances)
        print(f"  Merged VOX scene saved to {output_file}")
    else:
        print("  Skipping VOX merge (use --merge to enable).")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compose a scene from a layout JSON.")
    parser.add_argument("layout", help="Path to the layout JSON file.")
    parser.add_argument("output", nargs="?", help="Optional path to the output VOX file.")
    parser.add_argument("--merge", action="store_true", help="Merge all assets into a single VOX file.")
    
    args = parser.parse_args()
    run_composer(args.layout, args.output, args.merge)
