import json
import os
import random

def create_layout():
    random.seed(42)
    layout = []

    # --- Structural (5x4 Grid: 400x320) ---
    # Floor (3x2 floor tiles covering 480x320, cropped to 400x320)
    for x_idx in range(3):
        for y_idx in range(2):
            layout.append({"asset_id": "wooden_floor", "pos": [x_idx * 160, y_idx * 160, -2], "rot": 0})

    # North Wall (Back) - Full height, hide nothing
    for x in range(0, 448, 64):
        layout.append({"asset_id": "timber_wall", "pos": [x, 308, 0], "rot": 0})
    
    # East Wall (Side) - Full height
    for y in range(0, 320, 64):
        layout.append({"asset_id": "timber_wall", "pos": [390, y, 0], "rot": 90})

    # Note: South and West walls are removed per Dollhouse Strategy.

    # --- Mezzanine (North and East Walls) ---
    # North side walkway
    for x in range(0, 320, 160):
        layout.append({"asset_id": "walkway_tile", "pos": [x, 256, 80], "rot": 0})
    # East side walkway
    layout.append({"asset_id": "walkway_tile", "pos": [256, 0, 80], "rot": 90})
    layout.append({"asset_id": "walkway_tile", "pos": [256, 160, 80], "rot": 90})
    # Corner
    layout.append({"asset_id": "walkway_tile", "pos": [256, 256, 80], "rot": 0})

    # Railings
    layout.append({"asset_id": "railing_long", "pos": [39, 255, 80], "rot": 0})
    layout.append({"asset_id": "railing_long", "pos": [139, 255, 80], "rot": 0})
    layout.append({"asset_id": "railing_long", "pos": [255, -1, 80], "rot": 90})
    layout.append({"asset_id": "railing_long", "pos": [255, 159, 80], "rot": 90})

    # Stairs (Ascending against East wall)
    layout.append({"asset_id": "stairs", "pos": [265, 95, 0], "rot": 0}) 
    layout.append({"asset_id": "stair_railing", "pos": [264, 95, 0], "rot": 270}) 

    # --- Key Features ---
    # Fireplace (Against East Wall)
    layout.append({"asset_id": "stone_fireplace", "pos": [382, 133, 0], "rot": 90})
    layout.append({"asset_id": "stone_pillar", "pos": [382, 133, 0], "rot": 0})

    # Bar Area (North-West Corner)
    layout.append({"asset_id": "bar_counter", "pos": [20, 240, 0], "rot": 0})
    for i in range(4):
        x = 30 + i * 30
        layout.append({"asset_id": "barstool", "pos": [x, 226, 0], "rot": random.randint(-10, 10)})
        layout.append({"asset_id": "bottle", "pos": [x + 4, 249, 38], "rot": random.randint(0, 360)})

    # Table Groups
    def add_table_group(bx, by):
        layout.append({"asset_id": "ornate_rug", "pos": [bx + 9, by - 17, 0.1], "rot": 0})
        layout.append({"asset_id": "medieval_feast_table", "pos": [bx, by, 0], "rot": 0})
        chairs = [(bx + 7, by + 21, 0), (bx + 43, by + 21, 0), (bx + 7, by - 3, 180), (bx + 43, by - 3, 180)]
        for cx, cy, crot in chairs:
            layout.append({"asset_id": "chair", "pos": [cx, cy, 0], "rot": crot + random.randint(-10, 10)})
        layout.append({"asset_id": "chandelier", "pos": [bx + 32, by + 16, 70], "rot": 0})
        layout.append({"asset_id": "candles", "pos": [bx + 20, by + 10, 24], "rot": 0})

    add_table_group(150, 140) # Center Stage
    add_table_group(300, 240) # North-East corner

    # --- Metadata ---
    # Units (Balanced in the Stage Rows)
    # Team 1 (South Stage: L/M)
    team1_units = [[120, 100, 0, 1.57], [160, 80, 0, 1.57], [200, 100, 0, 1.57]]
    # Team 2 (North Stage: M/N)
    team2_units = [[120, 220, 0, -1.57], [160, 240, 0, -1.57], [200, 220, 0, -1.57]]

    # Camera (Anchor Q, pointing N-NE)
    camera = { 
        "eye": [120, -179, 135], 
        "center": [160, 160, 0], 
        "angle": 3.5, 
        "distance": 365,
        "height": 135,
        "fov": 45 
    }

    # Auto-generate lights from candles/chandeliers
    lights = []
    lights.append({ "position": [360, 133, 40], "color": [1.0, 0.6, 0.2], "intensity": 50.0, "radius": 1500 }) # Fireplace
    
    for item in layout:
        if item["asset_id"] == "chandelier":
            lights.append({ "position": [item["pos"][0], item["pos"][1], 60], "color": [1.0, 0.95, 0.8], "intensity": 30.0, "radius": 1200 })
        elif item["asset_id"] == "candles":
            lights.append({ "position": [item["pos"][0], item["pos"][1], 30], "color": [1.0, 0.7, 0.4], "intensity": 8.0, "radius": 600 })

    scene_def = {
        "layout": layout, "lights": lights, "team1_units": team1_units, "team2_units": team2_units,
        "camera": camera, "sunDirection": [0.33, -0.39, 0.29],
        "ambientColor": [0.2, 0.2, 0.3], "fogColor": [0.1, 0.1, 0.15], "fogNear": 300, "fogFar": 1000
    }

    output_path = os.path.join(os.path.dirname(__file__), "../csg/tavern_layout.json")
    with open(output_path, "w") as f:
        json.dump(scene_def, f, indent=2)
    print(f"Generated Tavern layout (Dollhouse visibility).")

if __name__ == "__main__":
    create_layout()
