import json

def check(path):
    with open(path) as f:
        data = json.load(f)
    min_x, max_x = 999, -999
    min_y, max_y = 999, -999
    for i in data.get('instructions', []):
        if i.get('op') != 'add': continue
        p = i.get('pos', [0,0,0])
        s = i.get('size', [0,0,0])
        min_x = min(min_x, p[0])
        max_x = max(max_x, p[0]+s[0])
        min_y = min(min_y, p[1])
        max_y = max(max_y, p[1]+s[1])
    print(f"{path}: X {min_x}..{max_x} (Center {(min_x+max_x)/2})")

check('csg/bar_corner_64.json')
check('csg/bar_straight_64.json')
