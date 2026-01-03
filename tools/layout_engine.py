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
            "shelf": (65, 11, 58),
            "railing_long": (162, 3, 15),
            "railing_short": (82, 3, 15),
            "stair_railing": (162, 3, 95),
            "walkway_tile": (160, 64, 2)
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
    
    # 1. GROUND FLOOR
    for x in [80, 240]:
        for y in [80, 240]: eng.add("wooden_floor", x, y, 0)

    # 2. WALLS (Flush with 320x320 edges)
    for x in [128, 192]: eng.add("timber_wall", x, 314, 0, rot=0)
    for y in [128, 192]: eng.add("timber_wall", 314, y, 0, rot=90)

    # 3. SECOND FLOOR MEZZANINE (64 width, at Z=80)
    # North Walkway (Y: 256 to 320, Center 288)
    for x in [80, 240]: eng.add("walkway_tile", x, 288, 80, rot=0)
    # Railing for North Walkway (Gap at X=0-40 for stairs)
    eng.add("railing_long", 120, 256, 82, rot=0)
    eng.add("railing_long", 240, 256, 82, rot=0)

    # East Walkway (X: 256 to 320, Center 288)
    for y in [80, 240]: eng.add("walkway_tile", 288, y, 80, rot=90)
    # Railing for East Walkway (Inner edge X=256)
    eng.add("railing_long", 256, 80, 82, rot=90)
    eng.add("railing_long", 256, 240, 82, rot=90)

    # 4. STAIRCASE (North-West Corner, Flush with West Wall)
    # Reach mezzanine (Y=256) at Z=80. 
    # Stair depth is 160, so starts at Y = 256 - 160 = 96.
    # Center Y = (96 + 256) / 2 = 176.
    eng.add("stairs", 20, 176, 0, rot=0)
    # Diagonal Railing (Rot 270 flips the slope to match rising North)
    eng.add("stair_railing", 40, 176, 0, rot=270)

    # 5. DOORS & DECOR
    eng.add("door", 314, 40, 0, rot=90) # Entrance
    eng.add("door", 100, 314, 80, rot=0)
    eng.add("door", 220, 314, 80, rot=0)
    eng.add("bar_counter", 260, 280, 0, rot=0)
    eng.add("shelf", 260, 314, 40, rot=0)
    for x in [240, 260, 280]: 
        eng.add("barstool", x, 265, 0, rot=0)
        eng.add("bottle", x, 284, 38, rot=0)
        eng.add("tankard", x+5, 284, 38, rot=0)

    # 6. SEATING (3 Table Groups)
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

    add_table_set(160, 140)
    add_table_set(80, 80)
    add_table_set(220, 80)

    # 7. EXTRAS
    eng.add("stone_fireplace", 314, 160, 0, rot=90)
    for x in [96, 224]: eng.add("window", x, 307, 68, rot=180)
    for y in [96, 224]: eng.add("window", 307, y, 68, rot=270)
    eng.add("weapon_rack", 40, 314, 0, rot=0)
    
    eng.save("csg/tavern_layout.json")

if __name__ == "__main__": build_tavern()
