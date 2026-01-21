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
    
    count = len(tiles_to_show)
    width = int(math.ceil(math.sqrt(count)))
    height = int(math.ceil(count / width))
    
    print(f"Generating showcase for {count} tiles (Grid {width}x{height})...")
    
    lua_output = os.path.join(OUTPUT_DIR, f"{name}.lua")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(lua_output, 'w') as f:
        f.write(f"-- Showcase: {name} ({count} tiles)\n")
        f.write("return {\n    tiles = {\n")
        
        for i, tid in enumerate(tiles_to_show):
            x = (i % width) * 2 # Spacing * 2 to leave gaps
            z = (i // width) * 2
            
            # Place the tile
            f.write(f"        {{ tile_id = '{tid}', pos = {{{x}, {z}}}, height = 0, rot = 0 }},\n")
            
            # Add floor underneath if it's not a floor itself (optional, for visibility)
            # if "floor" not in tile_reg[tid].get("tile_tags", []):
            #    f.write(f"        {{ tile_id = 'floor_wood_80', pos = {{{x}, {z}}}, height = -16, rot = 0 }},\n")

        f.write("    },\n    layout = {}\n}")
        
    print(f"Generated {lua_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="showcase")
    parser.add_argument("--theme", help="Filter by theme (e.g. tavern)")
    args = parser.parse_args()
    
    generate_showcase(args.name, args.theme)
