import os
import json
import glob

CSG_DIR = "csg"
REGISTRY_PATH = "csg/asset_registry.json"

def parse_asset_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    asset_data = {}
    
    # Extract Name (fallback to filename)
    asset_data['name'] = data.get('name', os.path.basename(filepath).replace(".json", ""))
    
    # Extract Tags
    asset_data['asset_tags'] = data.get('asset_tags', [])
    
    # Extract Snap Points (just the names)
    snaps = data.get('snap_points', {})
    asset_data['snap_points'] = list(snaps.keys())
    
    # Extract logic (Is it a collection or raw asset?)
    if 'layout' in data or isinstance(data, list):
        asset_data['type'] = 'collection'
    else:
        asset_data['type'] = 'raw'
        
    return asset_data

def build_registry():
    registry = {}
    for filepath in glob.glob(f"{CSG_DIR}/*.json"):
        if "registry.json" in filepath: continue
        
        asset_id = os.path.basename(filepath).replace(".json", "")
        
        try:
            registry[asset_id] = parse_asset_json(filepath)
        except Exception as e:
            # print(f"Error parsing {filepath}: {e}")
            pass
            
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"Asset Registry built with {len(registry)} items at {REGISTRY_PATH}")
    return registry

if __name__ == "__main__":
    build_registry()
