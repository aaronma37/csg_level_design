import json
import os
import re

TILE_REGISTRY = "csg_assets/tile_registry.json"
CSG_DIR = "csg"
TILES_DIR = "csg_assets/tiles"

def is_point_in_box(px, py, pz, box_pos, box_size):
    x, y, z = box_pos
    w, h, d = box_size
    # Check if point is inside the box bounds (X, Y plane)
    return (x <= px < x + w) and (y <= py < y + h) and (z <= pz < z + d)

def check_tile(tile_id, data):
    block_w, block_h = data.get("block_size", [1, 1])
    
    lua_path = os.path.join(TILES_DIR, f"{tile_id}.lua")
    if not os.path.exists(lua_path):
        print(f"[!] {tile_id}: Lua file missing.")
        return
    
    with open(lua_path, 'r') as f:
        content = f.read()
    
    # Extract the FIRST asset_id (assumed to be the base)
    m = re.search(r'''asset_id\s*=\s*['"]([^'"]+)['"]''', content)
    if not m:
        print(f"[!] {tile_id}: No asset_id found in layout.")
        return
    asset_id = m.group(1)
    
    json_path = os.path.join(CSG_DIR, f"{asset_id}.json")
    if not os.path.exists(json_path):
        print(f"[!] {tile_id}: Base asset {asset_id}.json not found in /csg.")
        return

    with open(json_path, 'r') as f:
        try:
            asset_data = json.load(f)
        except:
            print(f"[!] {tile_id}: Failed to parse {asset_id}.json")
            return
    
    instructions = asset_data.get("instructions", [])
    
    # Determine result string
    missing = []
    # Asset Origin (0,0) maps to Primary Tile Center.
    # Primary Tile Center is absolute (16, 16).
    # So relative center of cell (ix, iz) is (ix*32, iz*32).
    for iz in range(block_h):
        for ix in range(block_w):
            tx, ty = ix * 32, iz * 32
            
            found_floor = False
            for instr in instructions:
                if instr.get("op") == "add":
                    pos = instr.get("pos", [0,0,0])
                    size = instr.get("size", [1,1,1])
                    # Check Z=0 or Z=1 (Floor height standard)
                    if is_point_in_box(tx, ty, 0, pos, size) or is_point_in_box(tx, ty, 1, pos, size):
                        found_floor = True
                        break
            if not found_floor:
                missing.append(f"({ix},{iz})")

    if not missing:
        print(f"[OK] {tile_id} ({block_w}x{block_h})")
    else:
        print(f"[FAIL] {tile_id} ({block_w}x{block_h}) - Missing Floor at: {', '.join(missing)}")

def main():
    if not os.path.exists(TILE_REGISTRY):
        print("Registry not found.")
        return
        
    with open(TILE_REGISTRY, 'r') as f:
        registry = json.load(f)
        
    print(f"Auditing {len(registry)} tiles for floor coverage...")
    for tid, data in sorted(registry.items()):
        check_tile(tid, data)

if __name__ == "__main__":
    main()
