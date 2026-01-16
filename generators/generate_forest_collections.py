import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random

def generate_collections():
    print("Generating Forest Collections...")
    
    # Helper to scatter foliage
    def scatter_foliage(count=5, base_z=16):
        props = []
        # Weighted choices: lots of grass/flowers, fewer logs/rocks
        assets = ["shrub_small"] * 3 + \
                 ["flower_patch_red"] * 2 + \
                 ["flower_patch_blue"] * 2 + \
                 ["grass_patch"] * 5 + \
                 ["debris_stump"] * 2 + \
                 ["debris_log"] * 1 + \
                 ["debris_rock_moss"] * 2
                 
        for _ in range(count):
            type = random.choice(assets)
            x = random.randint(4, 60)
            y = random.randint(4, 60)
            rot = random.randint(0, 3) * 90
            props.append({"asset_id": type, "pos": [x, y, base_z], "rot": rot})
        return props

    def scatter_reeds(count=3, base_z=12): # Water level approx 12-14
        props = []
        for _ in range(count):
            x = random.randint(10, 54)
            y = random.randint(10, 54)
            rot = random.randint(0, 3) * 90
            props.append({"asset_id": "reeds_patch", "pos": [x, y, base_z], "rot": rot})
        return props

    # Helper for random grass tile
    def rnd_grass():
        return random.choice(["tile_grass", "tile_grass_var1", "tile_grass_var2"])

    # 1. Forest Tile A (Tree Center + Foliage)
    col_forest_a = [
        {"asset_id": rnd_grass(), "pos": [0, 0, 0], "rot": 0},
        {"asset_id": "willow_tree_xl", "pos": [32, 32, 16], "rot": 0}
    ] + scatter_foliage(8, 16)
    
    # 2. Forest Tile B (Tree Offset + Fence + Foliage)
    col_forest_b = [
        {"asset_id": rnd_grass(), "pos": [0, 0, 0], "rot": 0},
        {"asset_id": "willow_tree_xl", "pos": [16, 48, 16], "rot": 90},
        {"asset_id": "forest_fence", "pos": [48, 16, 16], "rot": 0}
    ] + scatter_foliage(6, 16)
    
    # 3. Forest Tile C (Hilly + Dense Foliage + No Tree)
    col_forest_c = [
        {"asset_id": "tile_grass_hills", "pos": [0, 0, 0], "rot": 0}
    ] + scatter_foliage(12, 16)
    
    # 4. River Straight
    col_river_s = [
        {"asset_id": "tile_river_straight", "pos": [0, 0, 0], "rot": 0}
    ] + scatter_foliage(2, 16) + scatter_reeds(5, 10)
    
    # 5. River Corner
    col_river_c = [
        {"asset_id": "tile_river_corner", "pos": [0, 0, 0], "rot": 0}
    ] + scatter_reeds(5, 10)
    
    # 6. Forest Meadow (Open, no trees)
    col_meadow = [
        {"asset_id": rnd_grass(), "pos": [0, 0, 0], "rot": 0}
    ] + scatter_foliage(10, 16)

    # 7. Plateau (High Ground)
    col_plateau = [
        {"asset_id": "tile_plateau", "pos": [0, 0, 0], "rot": 0},
        {"asset_id": "willow_tree_xl", "pos": [32, 32, 32], "rot": 0} # Tree at Z=32
    ] + scatter_foliage(5, 32) # Foliage at Z=32

    # 8. Cliff Straight
    col_cliff = [
        {"asset_id": "tile_cliff_straight", "pos": [0, 0, 0], "rot": 0}
    ]

    def save(name, data):
        path = os.path.join(os.path.dirname(__file__), f"../csg/{name}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {path}")

    save("collection_forest_tile_A", col_forest_a)
    save("collection_forest_tile_B", col_forest_b)
    save("collection_forest_tile_C", col_forest_c)
    save("collection_forest_meadow", col_meadow)
    save("collection_forest_plateau", col_plateau)
    save("collection_forest_cliff", col_cliff)
    save("collection_river_straight", col_river_s)
    save("collection_river_corner", col_river_c)

if __name__ == "__main__":
    generate_collections()
