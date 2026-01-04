import json
import os

def create_layout():
    layout = []

    # --- Structural ---
    # 2x2 Floor (320x320)
    for x in [0, 160]:
        for y in [0, 160]:
            layout.append({"asset_id": "wooden_floor", "pos": [x, y, 0], "rot": 0})

    # North Wall
    layout.append({"asset_id": "timber_wall", "pos": [0, 308, 0], "rot": 0})
    layout.append({"asset_id": "timber_wall", "pos": [64, 308, 0], "rot": 0})
    layout.append({"asset_id": "timber_wall", "pos": [128, 308, 0], "rot": 0})
    layout.append({"asset_id": "timber_wall", "pos": [192, 308, 0], "rot": 0})
    
    # East Wall
    layout.append({"asset_id": "timber_wall", "pos": [308, 0, 0], "rot": 90})
    layout.append({"asset_id": "timber_wall", "pos": [308, 64, 0], "rot": 90})
    layout.append({"asset_id": "timber_wall", "pos": [308, 128, 0], "rot": 90})
    layout.append({"asset_id": "timber_wall", "pos": [308, 192, 0], "rot": 90})

    # Mezzanine Walkway (North and East)
    layout.append({"asset_id": "walkway_tile", "pos": [0, 256, 80], "rot": 0})
    layout.append({"asset_id": "walkway_tile", "pos": [160, 256, 80], "rot": 0})
    layout.append({"asset_id": "walkway_tile", "pos": [256, 0, 80], "rot": 90})
    layout.append({"asset_id": "walkway_tile", "pos": [256, 160, 80], "rot": 90})

    # Railings
    layout.append({"asset_id": "railing_long", "pos": [39, 255, 82], "rot": 0})
    layout.append({"asset_id": "railing_long", "pos": [159, 255, 82], "rot": 0})
    layout.append({"asset_id": "railing_long", "pos": [255, -1, 82], "rot": 90})
    layout.append({"asset_id": "railing_long", "pos": [255, 159, 82], "rot": 90})

    # Stairs
    layout.append({"asset_id": "stairs", "pos": [0, 96, 0], "rot": 0})
    layout.append({"asset_id": "stair_railing", "pos": [39, 95, 0], "rot": 270})

    # Doors
    layout.append({"asset_id": "door", "pos": [311, 24, 0], "rot": 90})
    layout.append({"asset_id": "door", "pos": [84, 311, 80], "rot": 0})
    layout.append({"asset_id": "door", "pos": [204, 311, 80], "rot": 0})

    # Windows
    layout.append({"asset_id": "window", "pos": [82, 305, 68], "rot": 180})
    layout.append({"asset_id": "window", "pos": [210, 305, 68], "rot": 180})
    layout.append({"asset_id": "window", "pos": [305, 82, 68], "rot": 270})
    layout.append({"asset_id": "window", "pos": [305, 210, 68], "rot": 270})

    # Fireplace
    layout.append({"asset_id": "stone_fireplace", "pos": [300, 133, 0], "rot": 90})

    # --- Bar Area ---
    layout.append({"asset_id": "bar_counter", "pos": [228, 274, 0], "rot": 0})
    layout.append({"asset_id": "shelf", "pos": [228, 309, 40], "rot": 0})
    for i in range(3):
        x = 235 + i * 20
        layout.append({"asset_id": "barstool", "pos": [x, 260, 0], "rot": 0})
        layout.append({"asset_id": "bottle", "pos": [x + 4, 283, 38], "rot": 0})
        layout.append({"asset_id": "tankard", "pos": [x + 6, 281, 38], "rot": 0})

    # --- Table Groups ---
    # Moved to "Far Side" (Higher Y, pushed towards North wall but keeping space for mezzanine)
    # Walkway is at Y=256, so we'll place tables around Y=190
    def add_table_group(bx, by):
        layout.append({"asset_id": "ornate_rug", "pos": [bx + 9, by - 17, 1], "rot": 0})
        layout.append({"asset_id": "medieval_feast_table", "pos": [bx, by, 2], "rot": 0})
        # Chairs
        layout.append({"asset_id": "chair", "pos": [bx + 7, by + 21, 2], "rot": 0})
        layout.append({"asset_id": "chair", "pos": [bx + 43, by + 21, 2], "rot": 0})
        layout.append({"asset_id": "chair", "pos": [bx + 7, by - 3, 2], "rot": 180})
        layout.append({"asset_id": "chair", "pos": [bx + 43, by - 3, 2], "rot": 180})
        # Props
        layout.append({"asset_id": "tankard", "pos": [bx + 13, by + 23, 25], "rot": 0})
        layout.append({"asset_id": "mug", "pos": [bx + 44, by + 24, 25], "rot": 0})
        # Lighting
        layout.append({"asset_id": "chandelier", "pos": [bx + 21, by + 4, 70], "rot": 0})

    # Three tables in a row along the far side
    add_table_group(60, 190)
    add_table_group(140, 190)
    add_table_group(220, 190)

    # Decorative
    layout.append({"asset_id": "weapon_rack", "pos": [22, 308, 0], "rot": 0})
    layout.append({"asset_id": "bookshelf", "pos": [130, 308, 0], "rot": 0})
    layout.append({"asset_id": "bookshelf", "pos": [180, 308, 0], "rot": 0})

    output_path = os.path.join(os.path.dirname(__file__), "../csg/tavern_layout.json")
    with open(output_path, "w") as f:
        json.dump(layout, f, indent=2)
    print(f"Generated layout with {len(layout)} items.")

if __name__ == "__main__":
    create_layout()
