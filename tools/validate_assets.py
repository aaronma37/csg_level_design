import os
import json
import re

TILE_REGISTRY = "csg_assets/tile_registry.json"
TILES_DIR = "csg_assets/tiles"
ASSETS_DIR = "csg_assets"

def parse_lua_assets(content):
    # Regex to find asset_id = 'name'
    return re.findall(r'''asset_id\s*=\s*['"]([^'"]+)['"]''', content)

def check():
    with open(TILE_REGISTRY, 'r') as f:
        registry = json.load(f)
        
    print(f"Checking {len(registry)} tiles...")
    
    missing_assets = set()
    
    for tile_id in registry:
        lua_path = os.path.join(TILES_DIR, f"{tile_id}.lua")
        if not os.path.exists(lua_path):
            print(f"MISSING TILE FILE: {lua_path}")
            continue
            
        with open(lua_path, 'r') as f:
            content = f.read()
            
        assets = parse_lua_assets(content)
        for aid in assets:
            gltf_path = os.path.join(ASSETS_DIR, f"{aid}.gltf")
            if not os.path.exists(gltf_path):
                print(f"MISSING ASSET: {aid}.gltf (referenced by {tile_id})")
                missing_assets.add(aid)

    if not missing_assets:
        print("All assets verified!")
    else:
        print(f"Found {len(missing_assets)} missing assets.")

if __name__ == "__main__":
    check()
