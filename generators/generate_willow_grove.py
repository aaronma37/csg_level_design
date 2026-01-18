import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random

def generate_layout():
    print("Generating 5x4 Willow Grove (400x320)...")
    random.seed(42) 
    
    TILE_SIZE = 64
    GRID_W, GRID_H = 7, 5 # approx 448x320, we crop to 400x320 conceptually
    
    layout = []
    
    for x in range(GRID_W):
        for y in range(GRID_H):
            pos = [x * TILE_SIZE, y * TILE_SIZE, 0]
            rot = random.choice([0, 90, 180, 270])
            
            if y == 2: # River Row (Center)
                layout.append({
                    "asset_id": "collection_river_straight",
                    "pos": [x * TILE_SIZE, 2 * TILE_SIZE, 0],
                    "rot": 90
                })
                continue

            asset_id = "collection_forest_meadow"
            if y < 2:
                asset_id = "tile_grass" if x == 3 else "collection_forest_meadow"
            elif y >= 3:
                asset_id = "collection_forest_cliff" if y == 3 else "collection_forest_plateau"
            
            layout.append({"asset_id": asset_id, "pos": pos, "rot": rot})

    # --- Metadata ---
    # Team 1 (Left Stage: L)
    team1_units = [[120, 100, 2, 270], [100, 120, 2, 270], [100, 80, 2, 270]]
    # Team 2 (Right Stage: N)
    team2_units = [[280, 100, 2, 90], [300, 120, 2, 90], [300, 80, 2, 90]]

    # Camera (Anchor Q: X=80..160, Y=0..80)
    camera = { 
        "eye": [120, -179, 135], 
        "center": [200, 160, 0], # Point between L/N
        "angle": 3.5, 
        "distance": 365,
        "height": 135,
        "fov": 40 
    }

    scene_def = {
        "layout": layout, "lights": [], "team1_units": team1_units, "team2_units": team2_units,
        "camera": camera, "sunDirection": [0.33, -0.39, 0.29]
    }

    output_path = os.path.join(os.path.dirname(__file__), "../csg/willow_grove_layout.json")
    with open(output_path, "w") as f:
        json.dump(scene_def, f, indent=2)
    print(f"Layout generated.")

if __name__ == "__main__":
    generate_layout()
