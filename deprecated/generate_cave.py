import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
import math
from tools.sdf_builder import SDFBuilder
from tools import units
import palette

def generate_cave():
    print("Generating Re-scaled High-Density Organic Cave...")
    
    # 1. SCALE CONFIGURATION
    # Interior height target: ~85 voxels (1.7 CU)
    interior_radius = int(units.CU * 1.1) # 55v radius
    exterior_radius = int(units.CU * 1.4) # 70v radius
    
    def cave_shell_sdf(p):
        # Exterior Mass
        res = SDFBuilder.sphere(p - np.array([0, 0, 30]), exterior_radius)
        # Add some side-bulges for organic feel
        res = SDFBuilder.smooth_union(res, SDFBuilder.sphere(p - np.array([40, 20, 30]), units.CU * 0.8), k=25)
        res = SDFBuilder.smooth_union(res, SDFBuilder.sphere(p - np.array([-40, -30, 40]), units.CU * 0.9), k=25)
        
        # Interior Carving
        # Shifted up to create room for the floor
        interior = SDFBuilder.sphere(p - np.array([0, 0, 45]), interior_radius)
        interior = SDFBuilder.smooth_union(interior, SDFBuilder.sphere(p - np.array([30, 10, 45]), units.CU * 0.6), k=15)
        
        # Surface roughness (Meso-detail)
        roughness = math.sin(p[0]*0.1) * math.cos(p[1]*0.1) * math.sin(p[2]*0.1) * 4.0
        
        return max(res + roughness, -interior)

    # Expanded bounds for the larger scale
    bounds_min = [-100, -100, -20]
    bounds_max = [100, 100, 120]
    
    print(f"  Sampling SDF (Target Interior Height: {interior_radius * 2} voxels)...")
    shell_voxels = SDFBuilder.generate_voxels(cave_shell_sdf, bounds_min, bounds_max)

    # 2. MICRO-DETAIL: Color Jittering
    stone_base, stone_dark, stone_light = [], [], []
    for v in shell_voxels:
        rand = np.random.random()
        if rand > 0.88: stone_light.append(v)
        elif rand < 0.15: stone_dark.append(v)
        else: stone_base.append(v)

    instructions = []
    
    # Add Shell
    for pts, color in [(stone_base, palette.STONE_BASE), 
                       (stone_dark, palette.STONE_DARK), 
                       (stone_light, palette.STONE_LIGHT)]:
        instructions.append({
            "op": "add", "shape": "point_cloud", "pos": [0, 0, 0],
            "points": pts, "color": color
        })

    # 3. MESO-DETAIL: Scaled Stalactites
    # Ceiling is roughly at Z=100
    stalactite_locs = [
        ([20, 20, 90], 10, 40),
        ([-30, 10, 85], 8, 30),
        ([5, -40, 88], 12, 45),
    ]
    for pos, r, h in stalactite_locs:
        instructions.append({
            "op": "add", "shape": "cone", "pos": pos,
            "radius_bottom": r, "radius_top": 0, "height": -h,
            "axis": "z", "color": palette.STONE_BASE
        })

    # 4. STRUCTURAL: Flatten Floor (Clearance check)
    # This will result in a floor at Z=15. Ceiling is at ~100.
    # Total clearance = 85 voxels.
    instructions.append({
        "op": "subtract", "shape": "cuboid",
        "pos": [-90, -90, -20], "size": [180, 180, 35]
    })
    
    # 5. Magic Crystals
    instructions.append({
        "op": "add", "shape": "cone", "pos": [40, 40, 15],
        "radius_bottom": 5, "radius_top": 0, "height": 12,
        "axis": "z", "color": palette.FIRE_GLOW
    })

    # 6. Save and Compile
    data = {"name": "high_density_cave", "instructions": instructions}
    output_path = os.path.join(os.path.dirname(__file__), "../csg/high_density_cave.json")
    with open(output_path, "w") as f:
        json.dump(data, f)
    print(f"Done! Saved {len(shell_voxels)} voxels to {output_path}")

if __name__ == "__main__":
    generate_cave()
