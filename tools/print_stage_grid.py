import sys
import os
import json
from collections import defaultdict

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools.lint_layout as linter

GRID_WIDTH = 400
GRID_HEIGHT = 320
CELL_SIZE = 80

CELL_MAP = [
    ['P', 'Q', 'R', 'S', 'T'], # Row 0
    ['K', 'L', 'M', 'N', 'O'], # Row 1
    ['F', 'G', 'H', 'I', 'J'], # Row 2
    ['A', 'B', 'C', 'D', 'E']  # Row 3
]

def get_cell_coords(x, y):
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    if not (0 <= col <= 4 and 0 <= row <= 3): return None, None
    return row, col

def visualize_layout(layout_file, save_file=None):
    if not os.path.exists(layout_file):
        print("Error: " + str(layout_file))
        return ""

    items = linter.load_layout_flattened(layout_file)
    grid_contents = defaultdict(list)
    
    for item in items:
        cx, cy = item['pos'][0], item['pos'][1]
        row, col = get_cell_coords(cx, cy)
        if row is not None:
            name = item['asset_id'].replace('collection_', '').replace('.json', '')
            grid_contents[(row, col)].append(name)

    # Load Units
    with open(layout_file, 'r') as f:
        data = json.load(f)
    
    units = []
    if isinstance(data, dict):
        for u in data.get('team1_units', []): units.append({'pos': u, 'name': 'T1_Unit'})
        for u in data.get('team2_units', []): units.append({'pos': u, 'name': 'T2_Unit'})
            
    for u in units:
        cx, cy = u['pos'][0], u['pos'][1]
        row, col = get_cell_coords(cx, cy)
        if row is not None:
            grid_contents[(row, col)].append(u['name'])

    # Build Output String
    out = ["Stage Grid Visualization: " + str(layout_file), ""]
    out.append("      North (Back)")
    out.append("   +----------------+----------------+----------------+----------------+----------------+")
    
    for row in range(3, -1, -1):
        lines = ["   |", "   |", "   |"]
        for col in range(5):
            cell_id = CELL_MAP[row][col]
            contents = grid_contents[(row, col)]
            
            # Line 0: Cell ID
            lines[0] += " " + cell_id.ljust(14) + " |"
            
            # Line 1: Content
            high_val = [x for x in contents if any(s in x for s in ['Unit', 'Hero', 'Bar', 'Fireplace', 'Door'])]
            others = [x for x in contents if x not in high_val]
            
            c_text = ""
            if high_val:
                c_text = ", ".join(high_val[:2])
            elif others:
                c_text = others[0]
            
            if len(c_text) > 14:
                c_text = c_text[:11] + "..."
            lines[1] += " " + c_text.ljust(14) + " |"
            
            # Line 2: Stats
            s_text = ""
            if len(contents) > 0:
                s_text = str(len(contents)) + " items"
            lines[2] += " " + s_text.ljust(14) + " |"
        
        out.extend(lines)
        out.append("   +----------------+----------------+----------------+----------------+----------------+")

    out.append("      South (Front)\n")
    final_ascii = "\n".join(out)
    
    # Print it
    print(final_ascii)
    
    # Save it
    if not save_file:
        save_file = layout_file.replace('.json', '.stage_grid.txt')
    
    with open(save_file, 'w') as f:
        f.write(final_ascii)
    
    print("ASCII Grid saved to: " + str(save_file))
    return final_ascii

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/print_stage_grid.py csg/layout.json")
    else:
        visualize_layout(sys.argv[1])
