import sys
import hashlib
import os
import json

CACHE_FILE = "csg_assets/.build_cache.json"

def get_file_hash(path):
    if not os.path.exists(path): return None
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_hash.py <asset_name>")
        sys.exit(1)

    asset_name = sys.argv[1]
    json_path = f"csg/{asset_name}.json"
    
    if not os.path.exists(json_path):
        # If no JSON exists (it's a raw VOX), we just say it needs update 
        # (or handle VOX hashing, but JSON is our source of truth for generators)
        print("update")
        return

    current_hash = get_file_hash(json_path)
    
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)

    if cache.get(asset_name) == current_hash and os.path.exists(f"csg_assets/{asset_name}.gltf"):
        print("skip")
    else:
        # Update cache
        cache[asset_name] = current_hash
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
        print("update")

if __name__ == "__main__":
    main()
