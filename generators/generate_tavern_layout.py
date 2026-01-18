import json
import os
import random

def create_layout():
    random.seed(42)
    layout = []

    # Floor (3x2 floor tiles)
    for x_idx in range(3):
        for y_idx in range(2):
            layout.append({"asset_id": "wooden_floor", "pos": [x_idx * 160, y_idx * 160, -2], "rot": 0})

    # Walls
    for x in range(0, 448, 64):
        layout.append({"asset_id": "timber_wall", "pos": [x, 308, 0], "rot": 0})
    for y in range(0, 320, 64):
        layout.append({"asset_id": "timber_wall", "pos": [390, y, 0], "rot": 90})

    # Furniture
    layout.append({"asset_id": "stone_fireplace", "pos": [382, 133, 0], "rot": 90})
    layout.append({"asset_id": "bar_counter", "pos": [20, 240, 0], "rot": 0})

    def add_table_group(bx, by):
        layout.append({"asset_id": "medieval_feast_table", "pos": [bx, by, 0], "rot": 0})
        chairs = [(bx+7, by+21, 0), (bx+43, by+21, 0), (bx+7, by-3, 180), (bx+43, by-3, 180)]
        for cx, cy, crot in chairs:
            layout.append({"asset_id": "chair", "pos": [cx, cy, 0], "rot": crot + random.randint(-10, 10)})

    add_table_group(180, 240)
    add_table_group(280, 100)

    # Metadata
    team1_units = [[180, 100, 0, 1.57], [200, 80, 0, 1.57], [220, 100, 0, 1.57]]
    team2_units = [[180, 220, 0, -1.57], [200, 240, 0, -1.57], [220, 220, 0, -1.57]]

    # Camera (Eye at P, centered between teams)
    camera = { 
        "eye": [40, -139, 135], 
        "center": [200, 160, 0], 
        "angle": 3.5, 
        "distance": 365,
        "height": 135,
        "fov": 45 
    }

    scene_def = {
        "layout": layout, "lights": [], "team1_units": team1_units, "team2_units": team2_units,
        "camera": camera, "sunDirection": [0.33, -0.39, 0.29],
        "ambientColor": [0.2, 0.2, 0.3], "fogColor": [0.1, 0.1, 0.15], "fogNear": 300, "fogFar": 1000
    }

    output_path = os.path.join(os.path.dirname(__file__), "../csg/tavern_layout.json")
    with open(output_path, "w") as f:
        json.dump(scene_def, f, indent=2)
    print(f"Generated Tavern layout.")

if __name__ == "__main__":
    create_layout()
