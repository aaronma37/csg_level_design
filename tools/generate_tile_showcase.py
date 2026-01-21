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
    
    with open(lua_output, 'w') as f:
        f.write(f"-- Showcase: {name} ({len(tiles_to_show)} tiles)\n")
        f.write("return {\n    tiles = {\n")
        
        cur_x = 0
        cur_z = 0
        max_z_in_row = 0
        row_width_limit = 10 # 10 tiles wide
        
        for tid in tiles_to_show:
            data = tile_reg[tid]
            bw, bh = data.get("block_size", [1, 1])
            
            # If we exceed row width, wrap to next row
            if cur_x + bw > row_width_limit:
                cur_x = 0
                cur_z += max_z_in_row + 1 # +1 for gap
                max_z_in_row = 0
            
            # Place the tile
            # We add a +0.5 offset if the engine treats coords as corners?
            # Actually, let's stick to integers and see if they overlap.
            f.write(f"        {{ tile_id = '{tid}', pos = {{{cur_x}, {cur_z}}}, height = 0, rot = 0 }},\n")
            
            # Update cursors
            cur_x += bw + 1 # +1 for gap
            max_z_in_row = max(max_z_in_row, bh)

        f.write("    },\n    layout = {}\n}")
        
    print(f"Generated {lua_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="showcase")
    parser.add_argument("--theme", help="Filter by theme (e.g. tavern)")
    args = parser.parse_args()
    
    generate_showcase(args.name, args.theme)
