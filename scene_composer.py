import struct
import json
import sys
import os
import palette # Import shared palette

# --- 1. HELPER: MagicaVoxel Chunk Writer ---
class VoxWriter:
    def __init__(self):
        self.palette = palette.PALETTE_COLORS
        self.models = [] # List of (size, voxels) tuples
        self.nodes = [] # List of node byte blocks
        self.next_node_id = 0

    def add_model(self, voxels):
        """
        voxels: list of (x, y, z, c)
        Returns: model_id
        """
        if not voxels:
            # Empty model placeholder
            self.models.append(((1,1,1), []))
            return len(self.models) - 1

        xs, ys, zs = zip(*[(v[0], v[1], v[2]) for v in voxels])
        min_x, min_y, min_z = min(xs), min(ys), min(zs)
        mx, my, mz = max(xs)-min_x+1, max(ys)-min_y+1, max(zs)-min_z+1
        
        # Normalize
        norm_voxels = [(v[0]-min_x, v[1]-min_y, v[2]-min_z, v[3]) for v in voxels]
        
        self.models.append(((mx, my, mz), norm_voxels))
        return len(self.models) - 1

    def _pack_string(self, s):
        b = s.encode('utf-8')
        return struct.pack('<I', len(b)) + b

    def _pack_dict(self, d):
        # Format: NumPairs (I) + (Key (String) + Value (String))...
        content = struct.pack('<I', len(d))
        for k, v in d.items():
            content += self._pack_string(str(k))
            content += self._pack_string(str(v))
        return content

    def _make_chunk(self, tag, content):
        return tag + struct.pack('<II', len(content), 0) + content

    def create_transform_node(self, child_node_id, translation=(0,0,0), rotation=0, layer_id=0):
        # nTRN
        node_id = self.next_node_id
        self.next_node_id += 1
        
        # Rotation byte:
        # 0: identity
        # standard magicavoxel rotation encoding is complex, assuming simplified 0-3 for now
        # Actually MagicaVoxel stores rotation as a byte.
        # Bits 0-1: index of row 0 (0=x, 1=y, 2=z)
        # Bits 2-3: index of row 1
        # ...
        # Standard: 4 (00000100) -> X Y Z ? No.
        # Let's stick to translation first. Rotation logic needs lookup.
        # 0 = identity.
        rot_byte = 0 
        # Simple lookup for Z-rotation
        if rotation == 90: rot_byte = (1 << 0) | (0 << 2) # Swap X/Y ?
        # MagicaVoxel Rotation is tricky without a library.
        # Use simple mapping if possible, or 0.
        # Valid rotation byte: (1<<0) | (2<<2) | (0<<4) | ...
        # Let's use a dictionary for common Z rotations if needed, or 0.
        # 0 is Identity.
        # 90 deg Z: R = [0 -1 0; 1 0 0; 0 0 1]
        # internal format:
        # bit 0-1: row 0 index (0=x, 1=y, 2=z) -> 1 (y)
        # bit 2-3: row 1 index -> 0 (x)
        # bit 4: row 0 neg -> 1 (neg)
        # bit 5: row 1 neg -> 0
        # bit 6: row 2 neg -> 0
        # row 2 index implied as remaining.
        # 90 deg: row0 is -y. row1 is x. row2 is z.
        # row0 idx=1 (y). bit0-1=1.
        # row1 idx=0 (x). bit2-3=0.
        # row0 neg? yes. bit4=1.
        # row1 neg? no. bit5=0.
        # byte: 1 | (0<<2) | (1<<4) = 1 | 16 = 17.
        
        rot_map = {
            0: 4,   # Identity (row0=x, row1=y) -> 0|1<<2 = 4? Wait.
                    # row0=0(x), row1=1(y). bits: 00 01. 0 | 4 = 4. Correct.
            90: 22, # 90 Z: x->y, y->-x.
                    # row0=y (1). row1=x (0).
                    # row0 sign +. row1 sign -.
                    # byte = 1 | (0<<2) | (0<<4) | (1<<5) = 1 | 32 = 33? 
                    # This is complex. Let's pass 'rotation' as a string in dictionary for now?
                    # No, nTRN uses a byte `_r`.
                    
                    # For now, let's implement just translation to be safe, or guess.
                    # MagicaVoxel 0.99a+ uses `_r` string in dictionary OR `rot` byte.
                    # Modern vox uses `_r` byte inside the content.
        }
        
        # Standard rotations (Z axis)
        # 0: 4
        # 90: 22 (from PyVox libraries)
        # 180: 21
        # 270: 38
        
        r_byte = 4
        if rotation == 90: r_byte = 22 # Approx
        elif rotation == 180: r_byte = 21 # Approx
        elif rotation == 270: r_byte = 38 # Approx
        
        # Make dictionary
        frames = []
        # Frame 0
        frame_dict = {
            "_t": f"{translation[0]} {translation[1]} {translation[2]}",
            "_r": f"{r_byte}" # nTRN uses string for transform??
            # Spec says:
            # DICT: node attributes
            # DICT: frame attributes (for each frame)
            #   _t : translation
            #   _r : rotation (byte as string? or just byte?)
            # Usually _r is a byte, but stored in the dictionary as a string value?
            # actually MagicaVoxel documentation says `_r` stores the rotation byte as a string (e.g. "4").
        }
        
        content = struct.pack('<I', node_id)
        content += self._pack_dict({}) # Node attributes
        content += struct.pack('<I', child_node_id)
        content += struct.pack('<I', 0) # Reserved
        content += struct.pack('<I', layer_id) # Layer ID
        content += struct.pack('<I', 1) # Num Frames
        content += self._pack_dict(frame_dict)
        
        return self._make_chunk(b'nTRN', content)

    def create_group_node(self, child_ids):
        # nGRP
        node_id = self.next_node_id
        self.next_node_id += 1
        
        content = struct.pack('<I', node_id)
        content += self._pack_dict({})
        content += struct.pack('<I', len(child_ids))
        for cid in child_ids:
            content += struct.pack('<I', cid)
            
        return self._make_chunk(b'nGRP', content)

    def create_shape_node(self, model_id):
        # nSHP
        node_id = self.next_node_id
        self.next_node_id += 1
        
        content = struct.pack('<I', node_id)
        content += self._pack_dict({})
        content += struct.pack('<I', 1) # Num Models
        content += struct.pack('<I', model_id)
        content += self._pack_dict({}) # Model Attributes
        
        return self._make_chunk(b'nSHP', content)

    def save(self, filename, scene_instances):
        """
        scene_instances: list of (model_index, pos, rot)
        """
        if not self.models:
            print("No models to save.")
            return

        print(f"Saving Scene with {len(self.models)} unique models and {len(scene_instances)} instances to {filename}...")
        
        chunks = b''
        
        # 1. Models (SIZE + XYZI)
        for size, voxels in self.models:
            chunks += self._make_chunk(b'SIZE', struct.pack('<III', *size))
            xyzi_content = struct.pack('<I', len(voxels))
            for v in voxels:
                 xyzi_content += struct.pack('<BBBB', *v)
            chunks += self._make_chunk(b'XYZI', xyzi_content)
            
        # 2. Scene Graph
        # Tree:
        # World (nTRN) -> Group (nGRP) -> [Instances (nTRN -> nSHP)]
        
        # Create Instance Nodes (Shape + Transform)
        instance_node_ids = []
        # We need to build bottom-up or just collect chunks?
        # Nodes are referenced by ID. Order in file doesn't strictly matter if IDs are valid, 
        # but usually defined before use or just listed.
        # We'll generate the chunks and append them.
        
        graph_chunks = []
        
        for model_idx, pos, rot in scene_instances:
            # Shape Node
            shp_chunk = self.create_shape_node(model_idx)
            shp_id = self.next_node_id - 1
            graph_chunks.append(shp_chunk)
            
            # Transform Node
            trn_chunk = self.create_transform_node(shp_id, pos, rot)
            trn_id = self.next_node_id - 1
            graph_chunks.append(trn_chunk)
            
            instance_node_ids.append(trn_id)
            
        # Group Node containing all instances
        grp_chunk = self.create_group_node(instance_node_ids)
        grp_id = self.next_node_id - 1
        graph_chunks.append(grp_chunk)
        
        # Root Transform
        root_chunk = self.create_transform_node(grp_id)
        # root_id = self.next_node_id - 1
        graph_chunks.append(root_chunk)
        
        # Add graph chunks (reversed? No, order doesn't matter much but root last is conventional)
        # Let's add them in creation order
        for c in graph_chunks:
            chunks += c
            
        # 3. Palette
        pal_content = b''
        for i in range(1, 256):
            if i < len(self.palette):
                pal_content += struct.pack('<BBBB', *self.palette[i])
            else:
                pal_content += struct.pack('<BBBB', 150, 150, 150, 255)
        chunks += self._make_chunk(b'RGBA', pal_content)
        
        # Write File
        with open(filename, 'wb') as f:
            f.write(b'VOX ' + struct.pack('<I', 150))
            f.write(b'MAIN' + struct.pack('<II', 0, len(chunks)) + chunks)

# --- 2. SCENE COMPOSER ---
def load_vox_data(filename):
    if not os.path.exists(filename):
        print(f"Error: Asset file '{filename}' not found.")
        return []

    voxels = []
    with open(filename, 'rb') as f:
        if f.read(4) != b'VOX ': return []
        f.read(4) # Version
        f.read(4) # MAIN
        f.read(4) # size
        f.read(4) # children
        
        while True:
            chunk_id = f.read(4)
            if len(chunk_id) < 4: break
            content_size = struct.unpack('<I', f.read(4))[0]
            children_size = struct.unpack('<I', f.read(4))[0]
            content = f.read(content_size)
            
            if chunk_id == b'XYZI':
                num_voxels = struct.unpack('<I', content[:4])[0]
                for i in range(num_voxels):
                    x, y, z, c = struct.unpack('<BBBB', content[4+i*4 : 4+(i+1)*4])
                    voxels.append((x, y, z, c))
            
            if children_size > 0:
                f.read(children_size)
    return voxels

def run_composer(layout_file, output_file="final_scene.vox"):
    with open(layout_file, 'r') as f:
        scene_data = json.load(f)
    
    writer = VoxWriter()
    
    # Cache loaded models: asset_id -> model_index
    loaded_models = {}
    
    scene_instances = []
    
    print(f"Composing Scene: {layout_file}")
    for item in scene_data:
        asset_id = item['asset_id']
        pos = item['pos']
        rot = item.get('rot', 0)
        
        if asset_id not in loaded_models:
            filename = f"{asset_id}.vox"
            voxels = load_vox_data(filename)
            model_idx = writer.add_model(voxels)
            loaded_models[asset_id] = model_idx
        
        model_idx = loaded_models[asset_id]
        scene_instances.append((model_idx, pos, rot))
        
    writer.save(output_file, scene_instances)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scene_composer.py scene_layout.json")
    else:
        run_composer(sys.argv[1])