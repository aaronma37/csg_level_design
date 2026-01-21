import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random
import math
import palette

def generate_foliage():
    print("Generating Detailed Foliage Assets...")
    
    def save(name, instructions):
        with open(os.path.join(os.path.dirname(__file__), f"../csg/{name}.json"), "w") as f:
            json.dump({"name": name, "instructions": instructions}, f)

    # 1. Detailed Shrub (Organic Cloud)
    shrub_instr = []
    points_by_col = {}
    
    # Grow from center
    for i in range(150):
        r = random.uniform(0, 6)
        theta = random.uniform(0, math.pi * 2)
        phi = random.uniform(0, math.pi)
        
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi) * 0.5 
        z += 3
        
        # Pick color from GRASS_RANGE
        # Higher Z -> Lighter Color
        idx = int((z / 6.0) * 10) % 10
        idx = max(0, min(9, idx))
        col = palette.GRASS_RANGE[idx]
        
        if col not in points_by_col: points_by_col[col] = []
        points_by_col[col].append([int(x), int(y), int(z)])
    
    for c, pts in points_by_col.items():
        shrub_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": pts, "color": c})
        
    save("shrub_small", shrub_instr)

    # 2. Detailed Grass Patch
    grass_instr = []
    points_by_col = {}
    
    for _ in range(12): # 12 blades
        bx = random.randint(-6, 6)
        by = random.randint(-6, 6)
        h = random.randint(3, 7)
        lean_x = random.randint(-1, 1)
        lean_y = random.randint(-1, 1)
        
        # Random base color for this blade
        blade_base_idx = random.randint(3, 8) # Lighter greens
        
        for k in range(h):
            idx = blade_base_idx
            if k > h-2: idx += 1 # Tip is lighter
            idx = min(9, idx)
            col = palette.GRASS_RANGE[idx]
            
            if col not in points_by_col: points_by_col[col] = []
            points_by_col[col].append([bx + (lean_x if k>2 else 0), by + (lean_y if k>2 else 0), k])
            
    for c, pts in points_by_col.items():
        grass_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": pts, "color": c})

    save("grass_patch", grass_instr)

    # 3. Detailed Flower Clump (Red)
    flower_instr = []
    
    # Generate 5 flowers
    for _ in range(5):
        fx = random.randint(-6, 6)
        fy = random.randint(-6, 6)
        h = random.randint(4, 6)
        
        # Stem (Green)
        stem_pts = [[fx, fy, z] for z in range(h)]
        flower_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": stem_pts, "color": palette.LEAF_BASE})
        
        # Petals (Red)
        petal_pts = []
        for ox in range(-1, 2):
            for oy in range(-1, 2):
                if abs(ox)+abs(oy) > 0: # Cross shape
                    petal_pts.append([fx+ox, fy+oy, h])
        flower_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": petal_pts, "color": palette.FABRIC_RED})
        
        # Center (Gold)
        flower_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": [[fx, fy, h+1]], "color": palette.FABRIC_GOLD})

    save("flower_patch_red", flower_instr)

    # 4. Blue Flower
    flower_b_instr = []
    for _ in range(5):
        fx = random.randint(-6, 6)
        fy = random.randint(-6, 6)
        h = random.randint(4, 6)
        
        stem_pts = [[fx, fy, z] for z in range(h)]
        flower_b_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": stem_pts, "color": palette.LEAF_BASE})
        
        petal_pts = []
        for ox in range(-1, 2):
            for oy in range(-1, 2):
                if abs(ox)+abs(oy) > 0:
                    petal_pts.append([fx+ox, fy+oy, h])
        flower_b_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": petal_pts, "color": palette.FABRIC_BLUE})
        flower_b_instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": [[fx, fy, h+1]], "color": palette.WHITE})

    save("flower_patch_blue", flower_b_instr)

    # 5. Reeds Patch (Water foliage)
    reeds_instr = []
    for _ in range(8):
        rx = random.randint(-4, 4)
        ry = random.randint(-4, 4)
        h = random.randint(6, 10)
        # Cattail head?
        # Stem
        reeds_instr.append({"op": "add", "shape": "cuboid", "pos": [rx, ry, -2], "size": [1, 1, h], "color": palette.LEAF_BASE})
        # Brown tip
        if random.random() > 0.5:
             reeds_instr.append({"op": "add", "shape": "cuboid", "pos": [rx, ry, h-3], "size": [2, 2, 3], "color": palette.WOOD_BROWN})
             
    save("reeds_patch", reeds_instr)

    print("Detailed Foliage generated.")

if __name__ == "__main__":
    generate_foliage()