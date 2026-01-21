import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import random
import math
import palette

def generate_debris():
    print("Generating Forest Debris...")
    
    def save(name, instructions):
        with open(os.path.join(os.path.dirname(__file__), f"../csg/{name}.json"), "w") as f:
            json.dump({"name": name, "instructions": instructions}, f)

    # 1. Tree Stump
    stump_instr = []
    # Main body
    # Cylinder-ish stack
    for z in range(8):
        r = 6 - (z * 0.2)
        # Add roots at bottom
        if z < 3:
            # 4 Roots
            for i in range(4):
                angle = (i / 4.0) * math.pi * 2
                root_len = 8 - z*2
                rx = math.cos(angle) * root_len
                ry = math.sin(angle) * root_len
                stump_instr.append({"op": "add", "shape": "cuboid", "pos": [int(rx), int(ry), z], "size": [3, 3, 1], "color": palette.WOOD_DARK})
        
        # Trunk
        stump_instr.append({"op": "add", "shape": "cylinder", "pos": [0, 0, z], "radius": r, "height": 1, "color": palette.WOOD_DARK})
        
    # Jagged Top (Inner lighter wood)
    stump_instr.append({"op": "add", "shape": "cylinder", "pos": [0, 0, 8], "radius": 4, "height": 1, "color": palette.WOOD_BROWN})
    stump_instr.append({"op": "add", "shape": "cylinder", "pos": [1, 1, 9], "radius": 2, "height": 1, "color": palette.WOOD_BROWN})
    
    save("debris_stump", stump_instr)

    # 2. Fallen Log
    log_instr = []
    length = 24
    radius = 4
    
    # Horizontal log along X
    # Slight arch? No, lie flat but maybe rotated slightly in collection.
    # Let's make it hollow/broken at one end.
    
    for x in range(-length//2, length//2):
        # Noise for bark texture?
        c = palette.WOOD_DARK if x % 4 != 0 else palette.WOOD_BROWN
        
        # Circle at this X
        for y in range(-radius, radius+1):
            for z in range(-radius, radius+1):
                if y*y + z*z <= radius*radius:
                    # Bottom cut (buried)
                    if z > -2:
                        log_instr.append({"op": "add", "shape": "cuboid", "pos": [x, y, z+2], "size": [1, 1, 1], "color": c})
                        
                        # Add Moss on top
                        if z >= radius - 1 and random.random() > 0.6:
                             log_instr.append({"op": "add", "shape": "cuboid", "pos": [x, y, z+3], "size": [1, 1, 1], "color": palette.LEAF_BASE})

    save("debris_log", log_instr)

    # 3. Mossy Rock
    rock_instr = []
    # Base blob
    for _ in range(3):
        # Overlapping spheres/ellipsoids
        rx = random.randint(-2, 2)
        ry = random.randint(-2, 2)
        sz = [random.randint(6, 10), random.randint(6, 10), random.randint(4, 7)]
        
        rock_instr.append({"op": "add", "shape": "ellipsoid", "pos": [rx, ry, 2], "size": sz, "color": palette.STONE_BASE})
        
        # Moss cap
        rock_instr.append({"op": "add", "shape": "ellipsoid", "pos": [rx, ry, 2 + sz[2]//2], "size": [sz[0]-1, sz[1]-1, 2], "color": palette.LEAF_BASE})

    save("debris_rock_moss", rock_instr)
    print("Debris generated.")

if __name__ == "__main__":
    generate_debris()
