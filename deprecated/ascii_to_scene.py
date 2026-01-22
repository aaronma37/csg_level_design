import argparse
import re
import os
import sys
import json

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def parse_properties(prop_str):
    props = {}
    if not prop_str: return props
    pairs = re.findall(r'(\w+)=([^,\s}]+)', prop_str)
    for k, v in pairs:
        try:
            if '.' in v: props[k] = float(v)
            else: props[k] = int(v)
        except:
            props[k] = v
    return props

def parse_file(path, legend, grid):
    if not os.path.exists(path):
        print(f"Error: File not found {path}")
        return
    with open(path, 'r') as f:
        lines = f.readlines()
    sect = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'): continue
        if line.startswith('#') and '=' not in line: continue
        
        if line.startswith('THEME'):
            parts = line.split('=')
            if len(parts) >= 2:
                t_path = parts[1].strip()
                if not os.path.exists(t_path):
                    t_path = os.path.join(os.path.dirname(path), t_path)
                if os.path.exists(t_path):
                    parse_file(t_path, legend, None)
                else:
                    print(f"Error: Theme file not found: {t_path}")
            continue
            
        if line in ['LEGEND', 'GRID']:
            sect = line
            continue
        if sect == 'LEGEND':
            m = re.match(r'^(\S+)\s*=\s*([^{]+)(?:\{(.*)\})?', line)
            if m:
                k, tid, prs = m.groups()
                legend[k] = {'tile_id': tid.strip(), **parse_properties(prs)}
        elif sect == 'GRID' and grid is not None:
            grid.append(line.split())

# --- Main Execution ---

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output", nargs='?')
args = parser.parse_args()

input_path = args.input
output_path = args.output or os.path.splitext(input_path)[0] + ".lua"

tile_reg = load_json("csg_assets/tile_registry.json")
legend = {}
grid = []
parse_file(input_path, legend, grid)

# 1. Validate Legend against Registry
has_errors = False
for key, info in legend.items():
    tid = info['tile_id']
    if tid.upper() in ['SKIP', 'EMPTY', 'NONE']:
        continue
    if tile_reg and tid not in tile_reg:
        print(f"Error in LEGEND: Tile ID '{tid}' (Key: {key}) not found in tile_registry.json")
        has_errors = True

if not grid:
    print("Error: No GRID section found in input file.")
    sys.exit(1)

lua_tiles = []
# 2. Process Grid and Validate Keys
for z, row in enumerate(grid):
    for x, key in enumerate(row):
        # Handle special built-in keys
        if key in ['-', 'SKIP', 'EMPTY']:
            continue
            
        info = legend.get(key)
        rot_off = 0
        
        # Check for rotation suffix (e.g. #1)
        if not info and len(key) > 1 and key[-1].isdigit():
            base, digit = key[:-1], int(key[-1])
            if base in legend and 0 <= digit <= 3:
                info, rot_off = legend[base], digit * 90
        
        if not info:
            if key == '.':
                print(f"Error at ({x}, {z}): Character '.' used but not defined in LEGEND (usually used for floor).")
            else:
                print(f"Error at ({x}, {z}): Unknown key '{key}' not found in LEGEND.")
            has_errors = True
            continue
            
        tid = info['tile_id']
        if tid.upper() in ['SKIP', 'EMPTY']:
            continue
            
        rot = info.get('rot', 0) + rot_off
        lua_tiles.append(f"        {{ tile_id='{tid}', pos={{{x}, {z}}}, rot={rot} }},")

if has_errors:
    print("\nScene conversion failed due to validation errors. Lua file not updated.")
    sys.exit(1)

# Generate Lua
lua_output = [
    f"-- Generated from {os.path.basename(input_path)}",
    "return {",
    "    tiles = {",
    "\n".join(lua_tiles),
    "    },",
    "    layout = {}",
    "}"
]

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    f.write("\n".join(lua_output))
print(f"Success! Saved to {output_path}")
