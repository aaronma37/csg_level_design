import os
import struct

def get_vox_size(filename):
    try:
        with open(filename, 'rb') as f:
            if f.read(4) != b'VOX ': return None
            f.read(4) # version
            while True:
                chunk_id = f.read(4)
                if not chunk_id: break
                content_size = struct.unpack('<I', f.read(4))[0]
                children_size = struct.unpack('<I', f.read(4))[0]
                if chunk_id == b'SIZE':
                    return struct.unpack('<III', f.read(12))
                else:
                    f.read(content_size)
    except:
        return None

def main():
    vox_dir = "vox"
    registry = {}
    for f in os.listdir(vox_dir):
        if f.endswith(".vox"):
            size = get_vox_size(os.path.join(vox_dir, f))
            if size:
                name = f.replace(".vox", "")
                registry[name] = size
    
    import json
    print(json.dumps(registry, indent=2))

if __name__ == "__main__":
    main()
