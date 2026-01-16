import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
import math
import random
import palette

def generate_willow_blocky():
    print("Generating Blocky Willow Tree (No SDF)...")
    
    # Target Height: 110
    # Trunk Height: ~70
    # Canopy Top: ~110
    
    instructions = []
    
    # 1. TRUNK (Stack of disks)
    h_trunk = 70
    base_r = 10
    top_r = 3
    
    trunk_voxels = []
    
    for z in range(h_trunk):
        progress = z / h_trunk
        # Taper
        r = base_r * (1.0 - progress) + top_r * progress
        # Wobble
        cx = int(math.sin(z * 0.1) * 3.0)
        cy = int(math.cos(z * 0.08) * 3.0)
        
        # Draw Disk
        r_int = int(r)
        r2 = r*r
        for dy in range(-r_int, r_int + 1):
            for dx in range(-r_int, r_int + 1):
                if dx*dx + dy*dy <= r2:
                    trunk_voxels.append([cx + dx, cy + dy, z])
                    
    instructions.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": trunk_voxels, "color": palette.WOOD_DARK})
    
    # 2. BRANCHES (Lines)
    # Distribute branches along the top section of the trunk
    num_branches = 16 # Increased count
    
    # Define trunk_top for crown placement later
    trunk_top = [int(math.sin(h_trunk * 0.1) * 3.0), int(math.cos(h_trunk * 0.08) * 3.0), h_trunk]
    
    for i in range(num_branches):
        # Random height for branch start (Top 25 voxels)
        z_start = h_trunk - int(np.random.triangular(0, 25, 25)) # Bias towards top
        
        # Calculate trunk center at this Z (reusing wobble logic)
        cx = int(math.sin(z_start * 0.1) * 3.0)
        cy = int(math.cos(z_start * 0.08) * 3.0)
        p0 = [cx, cy, z_start]
        
        # Random Angle (Golden Angle approx for even packing, plus noise)
        angle = i * 2.4 + random.uniform(-0.5, 0.5) 
        
        # Branch Curve: Out and Up, then Down
        length = 40 + np.random.randint(0, 25)
        
        # Control points
        # P1: Up and Out
        p1_x = p0[0] + math.cos(angle) * (length * 0.4)
        p1_y = p0[1] + math.sin(angle) * (length * 0.4)
        p1_z = p0[2] + 15 + np.random.randint(0, 15) # Arch peak varies
        
        # P2: Far Out and Down
        p2_x = p0[0] + math.cos(angle) * length
        p2_y = p0[1] + math.sin(angle) * length
        p2_z = p0[2] - 15 + np.random.randint(-10, 10) # Tip (drooping)
        
        # Interpolate Bezier (Quadratic)
        branch_voxels = []
        steps = 30
        for s in range(steps):
            t = s / steps
            itm_x = (1-t)*p0[0] + t*p1_x
            itm_y = (1-t)*p0[1] + t*p1_y
            itm_z = (1-t)*p0[2] + t*p1_z
            
            e_x = (1-t)*p1_x + t*p2_x
            e_y = (1-t)*p1_y + t*p2_y
            e_z = (1-t)*p1_z + t*p2_z
            
            x = int((1-t)*itm_x + t*e_x)
            y = int((1-t)*itm_y + t*e_y)
            z = int((1-t)*itm_z + t*e_z)
            
            # Thick Line
            thickness = 3 if t < 0.5 else 2
            for bx in range(-thickness//2, thickness//2 + 1):
                for by in range(-thickness//2, thickness//2 + 1):
                    for bz in range(-thickness//2, thickness//2 + 1):
                        branch_voxels.append([x+bx, y+by, z+bz])
            
            # 3. FOLIAGE DRAPES (Vertical columns from branch)
            if t > 0.4 and s % 2 == 0:
                # Draping probability
                if np.random.random() > 0.3:
                    drape_len = int(30 + np.random.randint(0, 40))
                    # Stop at floor (z=0)
                    floor_clearance = z - drape_len
                    if floor_clearance < 2:
                        drape_len = max(0, z - 2)
                    
                    if drape_len > 5:
                        leaf_col = palette.LEAF_BRIGHT if np.random.random() > 0.5 else palette.LEAF_LIGHT
                        
                        # Drunk Walk Vine
                        cur_x, cur_y, cur_z = x + np.random.randint(-2, 2), y + np.random.randint(-2, 2), z
                        
                        vine_points = []
                        for k in range(drape_len):
                            # Wobble
                            if k % 3 == 0: # Change direction every 3 voxels
                                cur_x += np.random.randint(-1, 2)
                                cur_y += np.random.randint(-1, 2)
                            
                            cur_z -= 1
                            vine_points.append([cur_x, cur_y, cur_z])
                            
                            # Thickness (2x2)
                            vine_points.append([cur_x+1, cur_y, cur_z])
                            vine_points.append([cur_x, cur_y+1, cur_z])
                            vine_points.append([cur_x+1, cur_y+1, cur_z])

                        instructions.append({
                            "op": "add", "shape": "point_cloud", 
                            "pos": [0,0,0], "points": vine_points, "color": leaf_col
                        })

        instructions.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": branch_voxels, "color": palette.WOOD_DARK})

    # Crown removed to prevent floating blob look.
    # The branches themselves provide enough canopy density now.

    with open(os.path.join(os.path.dirname(__file__), "../csg/willow_tree_xl.json"), "w") as f:
        json.dump({"name": "willow_tree_xl", "instructions": instructions}, f)
    print("Blocky Willow Generated.")

if __name__ == "__main__":
    generate_willow_blocky()