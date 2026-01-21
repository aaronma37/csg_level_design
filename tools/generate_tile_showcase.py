import json
import os
import math
import argparse
from themes import THEMES

TILE_REGISTRY_PATH = "csg_assets/tile_registry.json"
OUTPUT_DIR = "csg_assets/scenes"

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r') as f: return json.load(f)

def query_registry_by_theme(registry, theme_name):
    if theme_name not in THEMES:
        print(f"Warning: Theme '{theme_name}' not found. Returning all tiles.")
        return list(registry.keys())
    
    theme = THEMES[theme_name]
    valid_keys = set()
    
    # Collect all tags mentioned in the theme
    target_tags = set()
    for role, rules in theme.items():
        if isinstance(rules, dict):
            # Single rule
            if "include" in rules: target_tags.update(rules["include"])
        elif isinstance(rules, list):
            # List of rules (features)
            for r in rules:
                if "include" in r: target_tags.update(r["include"])
    
    # Filter registry
    # This is a loose filter: Include tile if it matches ANY role's tag set roughly
    # Actually, simpler: just return everything that has tags intersecting the theme's interests
    # OR, strictly check each role.
    
    # Strict Approach: Iterate all roles, find candidates, add to set.
    for role, rules in theme.items():
        rule_list = rules if isinstance(rules, list) else [rules]
        for rule in rule_list:
            include = rule.get("include", [])
            exclude = rule.get("exclude", [])
            
            for tid, data in registry.items():
                tags = data.get('tile_tags', [])
                if include and not all(t in tags for t in include): continue
                if exclude and any(t in tags for t in exclude): continue
                valid_keys.add(tid)
                
    return list(valid_keys)

def generate_showcase(name, theme_filter=None):
    tile_reg = load_json(TILE_REGISTRY_PATH)
    
    if theme_filter:
        tiles_to_show = query_registry_by_theme(tile_reg, theme_filter)
    else:
        tiles_to_show = list(tile_reg.keys())
        
    tiles_to_show.sort() # Alphabetical order
    
    print(f"Generating showcase for {len(tiles_to_show)} tiles...")
    
    lua_output = os.path.join(OUTPUT_DIR, f"{name}.lua")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # First, group tiles into rows to calculate row heights
    rows = []
    current_row = []
    cur_x = 0
    max_h_in_row = 0
    row_width_limit = 10
    
    for tid in tiles_to_show:
        data = tile_reg[tid]
        bw, bh = data.get("block_size", [1, 1])
        
        if cur_x + bw > row_width_limit:
            rows.append((current_row, max_h_in_row))
            current_row = []
            cur_x = 0
            max_h_in_row = 0
            
        current_row.append({"tid": tid, "bw": bw, "bh": bh, "x": cur_x})
        cur_x += bw + 1
        max_h_in_row = max(max_h_in_row, bh)
        
    if current_row:
        rows.append((current_row, max_h_in_row))
    
    with open(lua_output, 'w') as f:
        f.write(f"-- Showcase: {name} ({len(tiles_to_show)} tiles)\n")
        f.write("return {\n    tiles = {\n")
        
        cur_z = 0
        for row_tiles, row_h in rows:
            for t in row_tiles:
                # Align centers in Z:
                # Target center Z = cur_z + (row_h - 1) / 2.0
                # Tile origin Z = target_center_z - (t["bh"] - 1) / 2.0
                # Simplified: adj_z = cur_z + (row_h - t["bh"]) / 2.0
                adj_z = cur_z + (row_h - t["bh"]) / 2.0
                f.write(f"        {{ tile_id = '{t['tid']}', pos = {{{t['x']}, {adj_z}}}, height = 0, rot = 0 }},\n")
            
            cur_z += row_h + 1

        f.write("    },\n    layout = {}\n}")
        
    print(f"Generated {lua_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="showcase")
    parser.add_argument("--theme", help="Filter by theme (e.g. tavern)")
    args = parser.parse_args()
    
    generate_showcase(args.name, args.theme)
