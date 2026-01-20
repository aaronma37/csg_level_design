import os
import re
import json

TILES_DIR = "csg_assets/tiles"
REGISTRY_PATH = "csg_assets/tile_registry.json"

def parse_lua_tile(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    tile_data = {}
    
    # Extract Name
    name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
    tile_data['name'] = name_m.group(1) if name_m else os.path.basename(filepath)
    
    # Extract Metadata fields
    # tile_tags = { ... }
    tags_m = re.search(r'tile_tags\s*=\s*\{([^}]+)\}', content)
    if tags_m:
        tags_raw = tags_m.group(1)
        # Handle both single and double quotes
        tags = re.findall(r'["\']([^"\']+)["\']', tags_raw)
        tile_data['tile_tags'] = tags
    else:
        tile_data['tile_tags'] = []
        
    # nav_mask
    nav_m = re.search(r'nav_mask\s*=\s*(\d+)', content)
    tile_data['nav_mask'] = int(nav_m.group(1)) if nav_m else 0
    
    # base_height
    height_m = re.search(r'base_height\s*=\s*(\d+)', content)
    tile_data['base_height'] = int(height_m.group(1)) if height_m else 0
    
    # block_size = {x, y}
    block_m = re.search(r'block_size\s*=\s*\{([^}]+)\}', content)
    if block_m:
        tile_data['block_size'] = [int(x.strip()) for x in block_m.group(1).split(',')]
    else:
        tile_data['block_size'] = [1, 1] # Default 1x1 grid cell

    return tile_data

def build_registry():
    registry = {}
    for filename in os.listdir(TILES_DIR):
        if not filename.endswith(".lua"):
            continue
        
        tile_id = filename.replace(".lua", "")
        filepath = os.path.join(TILES_DIR, filename)
        
        try:
            registry[tile_id] = parse_lua_tile(filepath)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"Registry built with {len(registry)} tiles at {REGISTRY_PATH}")
    return registry

def query_registry(registry, include_tags=None, exclude_tags=None, nav_mask=None):
    results = []
    for tile_id, data in registry.items():
        # Filter by nav_mask
        if nav_mask is not None and data['nav_mask'] != nav_mask:
            continue
            
        # Filter by include_tags (All must match)
        if include_tags:
            if not all(tag in data['tile_tags'] for tag in include_tags):
                continue
        
        # Filter by exclude_tags (None must match)
        if exclude_tags:
            if any(tag in data['tile_tags'] for tag in exclude_tags):
                continue
                
        results.append(tile_id)
    return results

if __name__ == "__main__":
    reg = build_registry()
    
    # Quick Test
    walkable_wood = query_registry(reg, include_tags=["walkable", "wood"])
    print(f"Sample Query (walkable + wood): {walkable_wood[:5]}")
