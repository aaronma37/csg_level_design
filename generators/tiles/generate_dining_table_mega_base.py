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

def generate_dining_table_mega_base():
    name = "dining_table_mega_base"
    instructions = []
    
    # 1. Floor: 4x 32x32 Tiles (2x2 block)
    floor_offsets = [[0, 0], [32, 0], [0, 32], [32, 32]]
    for off in floor_offsets:
        ox, oy = off
        floor_instr = floor_wood_plain.get_instructions(32, 32)
        instructions.extend(offset_instructions(floor_instr, [ox, oy, 0]))

    # 2. Table (Imported)
    # Block size is 64x64. Center is (32, 32) absolute.
    # NW Tile Center is (16, 16) absolute.
    # Asset Origin (0,0) is NW Tile Center.
    # So Table Center is [16, 16, 0] relative to Origin.
    table_path = os.path.join(os.path.dirname(__file__), '../../csg/medieval_feast_table.json')
    if os.path.exists(table_path):
        with open(table_path, 'r') as f:
            table_data = json.load(f)
            # Center the table in the 2x2 block
            instructions.extend(offset_instructions(table_data.get('instructions', []), [16, 16, 0]))
    
    # Save
    data = {
        "name": name,
        "asset_tags": ["base", "mega", "dining"],
        "instructions": instructions,
        "snap_points": {
            # Snap points for chairs 
            # North row: Y = 16 (table center) - 22 = -6
            "seat_1": {"pos": [0, -6, 0]},
            "seat_2": {"pos": [32, -6, 0]},
            # South row: Y = 16 + 22 = 38
            "seat_3": {"pos": [0, 38, 0]},
            "seat_4": {"pos": [32, 38, 0]},
            
            # Table Surface (Z=25)
            "clutter_center": {"pos": [16, 16, 25]},
            "clutter_left":   {"pos": [0, 16, 25]},
            "clutter_right":  {"pos": [32, 16, 25]}
        }
    }
    
    output_path = os.path.join(os.path.dirname(__file__), f"../../csg/{name}.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_dining_table_mega_base()
