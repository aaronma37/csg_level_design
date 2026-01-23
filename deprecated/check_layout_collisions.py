import json
import sys
import os

# Registry from actual VOX files (X, Y, Z dimensions)
REGISTRY = {
    "wooden_floor": (160, 160, 2),
    "timber_wall": (256, 13, 140),
    "ornate_rug": (47, 67, 1),
    "medieval_feast_table": (64, 32, 26),
    "chair": (15, 15, 29),
    "chandelier": (23, 24, 26),
    "stone_fireplace": (54, 28, 140),
    "weapon_rack": (37, 13, 33),
    "trophy_wall": (15, 8, 22),
    "skull": (9, 8, 11),
    "barrel": (21, 21, 22),
    "window": (29, 6, 33),
    "bar_counter": (69, 15, 39),
    "barstool": (11, 11, 24),
    "bottle": (3, 3, 8),
    "mug": (6, 5, 6),
    "tankard": (9, 7, 9),
    "stairs": (41, 161, 81),
    "door": (33, 6, 51),
    "shelf": (65, 11, 58),
    "railing_long": (163, 3, 16),
    "railing_short": (83, 3, 16),
    "stair_railing": (163, 3, 96),
    "walkway_tile": (161, 65, 2),
    "stone_pillar": (16, 16, 140),
    "timber_beam": (160, 16, 12)
}

def get_bbox(item):
    aid = item['asset_id']
    w, d, h = REGISTRY.get(aid, (1, 1, 1))
    rot = item.get('rot', 0)
    if rot == 90 or rot == 270:
        w, d = d, w
    
    # In layout_engine.py: x, y, z = cx - w // 2, cy - d // 2, cz
    # But some layouts might store the min corner directly.
    # Assuming the layout stores the bottom-left corner as 'pos'.
    x, y, z = item['pos']
    return {
        'min': [x, y, z],
        'max': [x + w, y + d, z + h],
        'id': aid
    }

def intersects(b1, b2):
    # Standard AABB intersection
    return (b1['min'][0] < b2['max'][0] and b1['max'][0] > b2['min'][0] and
            b1['min'][1] < b2['max'][1] and b1['max'][1] > b2['min'][1] and
            b1['min'][2] < b2['max'][2] and b1['max'][2] > b2['min'][2])

def check_collisions(layout_path):
    with open(layout_path, 'r') as f:
        layout = json.load(f)
    
    bboxes = [get_bbox(item) for item in layout]
    collisions = []
    
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            if intersects(bboxes[i], bboxes[j]):
                # Allow rug/floor intersections as they are expected
                if bboxes[i]['id'] == 'wooden_floor' or bboxes[j]['id'] == 'wooden_floor':
                    continue
                if bboxes[i]['id'] == 'ornate_rug' or bboxes[j]['id'] == 'ornate_rug':
                    # Rugs are at Z=1, floor is Z=0..2. This will intersect.
                    # We only care if rugs intersect with furniture other than floors.
                    # Actually, if both are at Z=1, they intersect.
                    pass
                
                collisions.append((i, bboxes[i], j, bboxes[j]))
    
    if not collisions:
        return "No collisions detected."
    
    report = [f"Found {len(collisions)} collisions:"]
    for i, b1, j, b2 in collisions:
        report.append(f" - {b1['id']} (idx {i}) intersects with {b2['id']} (idx {j})")
        report.append(f"   Pos1: {b1['min']} Pos2: {b2['min']}")
    
    return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_layout_collisions.py <layout.json>")
        sys.exit(1)
    print(check_collisions(sys.argv[1]))
