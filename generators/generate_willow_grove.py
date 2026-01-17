import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random

def generate_layout():
    print("Generating Willow Grove (Collection Layout)...")
    random.seed(1337) 
    
    TILE_SIZE = 64
    GRID_W, GRID_H = 8, 8
    
    layout = []
    
    # River Path
    river_cells = [
        (4,0, "straight", 0), (4,1, "straight", 0), (4,2, "straight", 0), 
        (4,3, "corner", 0),   # South -> East
        (5,3, "straight", 90), # East-West
        (6,3, "corner", 180), # West -> North
        (6,4, "straight", 0), (6,5, "straight", 0), (6,6, "straight", 0), (6,7, "straight", 0)
    ]
    
    river_path = set()
    for rx, ry, type, rot in river_cells:
        river_path.add((rx, ry))
        asset = "collection_river_straight" if type == "straight" else "collection_river_corner"
        layout.append({
            "asset_id": asset,
            "pos": [rx * TILE_SIZE, ry * TILE_SIZE, 0],
            "rot": rot
        })
        
    # Fill rest with Forest
    for x in range(GRID_W):
        for y in range(GRID_H):
            if (x, y) not in river_path:
                asset_id = ""
                rot = 0
                if x < 3:
                    asset_id = "collection_forest_plateau"
                    rot = random.choice([0, 90, 180, 270])
                elif x == 3:
                    asset_id = "collection_forest_cliff"
                    rot = 0
                else:
                    choices = ["collection_forest_meadow"] * 6 + \
                              ["collection_forest_tile_A", "collection_forest_tile_B", "collection_forest_tile_C"] * 1
                    asset_id = random.choice(choices)
                    rot = random.choice([0, 90, 180, 270])
                
                layout.append({
                    "asset_id": asset_id,
                    "pos": [x * TILE_SIZE, y * TILE_SIZE, 0],
                    "rot": rot
                })
    
    # --- Metadata ---
    
    # Lights
    lights = []
    for _ in range(5):
        lx = random.randint(0, GRID_W * TILE_SIZE)
        ly = random.randint(0, GRID_H * TILE_SIZE)
        lz = 48 if lx < 3 * TILE_SIZE else 24 
        lights.append({
            "position": [lx, ly, lz + 10],
            "color": [0.4, 0.8, 1.0], 
            "intensity": 20.0,
            "radius": 400
        })

    # Units
    # Team 1 (Heroes) on River North (Cell 6,7 -> [384, 448]. Spawn slightly South of center [416, 460] to clear boundary)
    # Z=15 for River Surface
    t1_rot = -1.57
    team1_units = [
        [416, 460, 15, t1_rot],
        [406, 450, 15, t1_rot],
        [426, 450, 15, t1_rot]
    ]
    
    # Team 2 (Enemies) on River Mid (Cell 6,4 -> [384, 256]. Spawn Center [416, 288])
    # Face North (1.57)
    t2_rot = 1.57
    team2_units = [
        [416, 288, 15, t2_rot],
        [406, 298, 15, t2_rot],
        [426, 298, 15, t2_rot]
    ]

    # Camera - Shifted South to avoid boundary clipping at the bottom of the screen
    # Center [416, 300] is within 100 units of Midpoint [416, 374]
    camera = {
        "eye": [416, 650, 300], 
        "center": [416, 300, 0],
        "fov": 40
    }

    scene_def = {
        "layout": layout,
        "lights": lights,
        "team1_units": team1_units,
        "team2_units": team2_units,
        "camera": camera,
        "ambientColor": [0.1, 0.1, 0.2],
        "fogColor": [0.05, 0.05, 0.1],
        "fogNear": 200,
        "fogFar": 1000
    }

    output_path = os.path.join(os.path.dirname(__file__), "../csg/willow_grove_layout.json")
    with open(output_path, "w") as f:
        json.dump(scene_def, f, indent=2)
    print(f"Layout generated with {len(layout)} tiles and full metadata.")

if __name__ == "__main__":
    generate_layout()