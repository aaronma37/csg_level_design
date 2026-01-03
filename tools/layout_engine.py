import json

class LayoutEngine:
    def __init__(self):
        self.instances = []
        self.registry = {
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
            "barrel": (19, 19, 22),
            "window": (28, 4, 32),
            "bar_counter": (64, 12, 38),
            "barstool": (11, 11, 24),
            "bottle": (3, 3, 8),
            "mug": (6, 5, 6),
            "tankard": (9, 7, 9),
            "stairs": (41, 161, 81),
            "door": (33, 6, 51),
            "shelf": (65, 11, 58)
        }

    def add(self, asset_id, cx, cy, cz, rot=0):
        w, d, h = self.registry.get(asset_id, (1, 1, 1))
        if rot == 90 or rot == 270: w, d = d, w
        x, y, z = cx - w // 2, cy - d // 2, cz
        self.instances.append({"asset_id": asset_id, "pos": [int(x), int(y), int(z)], "rot": rot})

    def save(self, path):
        with open(path, 'w') as f: json.dump(self.instances, f, indent=2)
        print(f"Layout saved to {path}")

def build_tavern():
    eng = LayoutEngine()
    
    # 1. GROUND FLOOR (320x320)
    for x in [80, 240]:
        for y in [80, 240]: eng.add("wooden_floor", x, y, 0)

    # 2. WALLS (Dollhouse)
    for x in [128, 192]: eng.add("timber_wall", x, 314, 0, rot=0)
    for y in [128, 192]: eng.add("timber_wall", 314, y, 0, rot=90)

    # 3. SECOND FLOOR WALKWAY (at Z=80)
    # North Walkway
    for x in [80, 240]: eng.add("wooden_floor", x, 280, 80)
    # East Walkway
    for y in [80, 240]: eng.add("wooden_floor", 280, y, 80)

    # 4. STAIRCASE (North-West Corner)
    eng.add("stairs", 30, 240, 0, rot=0)

    # 5. DOORS
    # Main Entrance (East Wall, Ground)
    eng.add("door", 314, 40, 0, rot=90)
    # Guest Room Doors (North Wall walkway, Upstairs)
    eng.add("door", 100, 314, 80, rot=0)
    eng.add("door", 220, 314, 80, rot=0)

    # 6. THE BAR AREA
    eng.add("bar_counter", 260, 280, 0, rot=0)
    eng.add("shelf", 260, 314, 40, rot=0) # Back-bar shelf
    for x in [240, 260, 280]: 
        eng.add("barstool", x, 265, 0, rot=0)
        eng.add("bottle", x, 284, 38, rot=0)
        eng.add("tankard", x+5, 284, 38, rot=0)

    # 7. SEATING (3 Table Groups)
    def add_table_set(cx, cy):
        eng.add("ornate_rug", cx, cy, 1)
        eng.add("medieval_feast_table", cx, cy, 2)
        eng.add("chair", cx-18, cy+16-4, 2, rot=0)
        eng.add("chair", cx+18, cy+16-4, 2, rot=0)
        eng.add("chair", cx-18, cy-16+4, 2, rot=180)
        eng.add("chair", cx+18, cy-16+4, 2, rot=180)
        eng.add("tankard", cx-15, cy+10, 25, rot=0)
        eng.add("mug", cx+15, cy+10, 25, rot=0)
        eng.add("chandelier", cx, cy, 70)

    add_table_set(160, 140) # Center
    add_table_set(80, 80)   # South-West
    add_table_set(220, 80)  # South-East

    # 8. DECOR
    eng.add("stone_fireplace", 314, 160, 0, rot=90)
    for x in [96, 224]: eng.add("window", x, 307, 68, rot=180)
    for y in [96, 224]: eng.add("window", 307, y, 68, rot=270)
    eng.add("weapon_rack", 40, 314, 0, rot=0)
    
    eng.save("csg/tavern_layout.json")

if __name__ == "__main__": build_tavern()