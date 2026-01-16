import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random

def generate_layout():
    print("Generating Willow Grove (Collection Layout)...")
    
    TILE_SIZE = 64
    GRID_W, GRID_H = 8, 8
    
    layout = []
    
    # Corrected River Path (South to North with an S-bend)
    # (4,0)-(4,2): North
    # (4,3): Turn East
    # (5,3): East
    # (6,3): Turn North
    # (6,4)-(6,7): North
    
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
        
    # Fill rest with Forest (Sparse)
    for x in range(GRID_W):
        for y in range(GRID_H):
            if (x, y) not in river_path:
                asset_id = ""
                rot = 0
                
                # Logic based on Column (Layering)
                if x < 3:
                    # High Plateau
                    asset_id = "collection_forest_plateau"
                    rot = random.choice([0, 90, 180, 270])
                elif x == 3:
                    # Cliff Line (High on West/Left -> Low on East/Right)
                    # Tile generated with High on Left. Rot 0.
                    asset_id = "collection_forest_cliff"
                    rot = 0
                else:
                    # Low Valley
                    choices = ["collection_forest_meadow"] * 6 + \
                              ["collection_forest_tile_A", "collection_forest_tile_B", "collection_forest_tile_C"] * 1
                    asset_id = random.choice(choices)
                    rot = random.choice([0, 90, 180, 270])
                
                layout.append({
                    "asset_id": asset_id,
                    "pos": [x * TILE_SIZE, y * TILE_SIZE, 0],
                    "rot": rot
                })
                
    output_path = os.path.join(os.path.dirname(__file__), "../csg/willow_grove_layout.json")
    with open(output_path, "w") as f:
        json.dump(layout, f, indent=2)
    print(f"Layout generated with {len(layout)} tiles.")

if __name__ == "__main__":
    generate_layout()