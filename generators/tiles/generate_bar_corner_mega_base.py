import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
from generators.floors import floor_wood_plain
import palette

def offset_instructions(instr_list, offset):
    new_list = []
    ox, oy, oz = offset
    for item in instr_list:
        new_item = item.copy()
        if 'pos' in new_item:
            px, py, pz = new_item['pos']
            new_item['pos'] = [px + ox, py + oy, pz + oz]
        new_list.append(new_item)
    return new_list

def generate():
    name = "bar_corner_mega_base"
    instructions = []
    
    # Floor: 2x2 (64x64)
    floor_offsets = [[0, 0], [32, 0], [0, 32], [32, 32]]
    for off in floor_offsets:
        ox, oy = off
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        instructions.extend(offset_instructions(floor_instr, [ox, oy, 0]))

    # Bar Corner (Imported)
    bar_path = os.path.join(os.path.dirname(__file__), '../../csg/bar_corner_64.json')
    if not os.path.exists(bar_path):
        # Fallback: create a simple L-shape block if source missing
        instructions.append({"op": "add", "pos": [0, 0, 0], "size": [64, 16, 24], "color": palette.WOOD_DARK})
        instructions.append({"op": "add", "pos": [0, 0, 0], "size": [16, 64, 24], "color": palette.WOOD_DARK})
    else:
        with open(bar_path, 'r') as f:
            bar_data = json.load(f)
            instructions.extend(offset_instructions(bar_data.get('instructions', []), [16, 16, 0]))
    
    # Save
    data = {
        "name": name,
        "asset_tags": ["base", "mega", "bar"],
        "instructions": instructions,
        "snap_points": {
            "center": {"pos": [16, 16, 0]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), f"../../csg/{name}.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate()
