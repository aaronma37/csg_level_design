import re

def parse(content):
    layout_match = re.search(r'layout\s*=\s*\{(.*)\}', content, re.DOTALL)
    if not layout_match: return "No layout"
    
    layout_str = layout_match.group(1)
    print(f"Layout Str: '{layout_str}'")
    
    raw_items = layout_str.split('},')
    print(f"Items: {len(raw_items)}")
    
    for raw in raw_items:
        clean = raw.strip().strip('{').strip()
        if not clean: continue
        print(f"Clean: '{clean}'")
        
        pos_m = re.search(r"pos\s*=\s*\{([^}]+)\}", clean)
        if pos_m:
            print(f"Pos Match: {pos_m.group(1)}")
        else:
            print("Pos NO MATCH")

test_lua = """
return {
    layout = {
        { asset_id = "wall_mega_plaster_A_part1", pos = {96, 0, 0}, rot = 0 }
    }
}
"""

parse(test_lua)
