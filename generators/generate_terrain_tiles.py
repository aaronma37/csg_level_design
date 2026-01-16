import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
import palette

def generate_tiles():
    print("Generating Layered Terrain Tiles...")
    
    W, D, H = 64, 64, 48 # Increased height for cliffs
    LOW_H = 16
    HIGH_H = 32
    
    def make_tile(name, type="flat"):
        voxels_grass = []
        voxels_dirt = []
        voxels_water = []
        
        for x in range(W):
            for y in range(D):
                # Distance from center (0 to 1) for edge masking
                nx, ny = x/W, y/D
                cx, cy = abs(nx - 0.5)*2, abs(ny - 0.5)*2
                dist_edge = max(cx, cy)
                edge_mask = 1.0 - (dist_edge ** 4)
                
                # Base Height calculation
                base = LOW_H
                is_cliff = False
                
                if type == "plateau":
                    base = HIGH_H
                    # Noise on top
                    noise = int(np.sin(x*0.4) * np.cos(y*0.4) * 1.5 * edge_mask)
                    base += noise
                    
                elif type == "cliff_straight":
                    # Transition from HIGH (x=0) to LOW (x=63)
                    # Steep drop around x=32
                    
                    # Cliff profile: S-curve or sharp drop
                    # Let's do a noisy cliff face
                    cliff_x = 32 + int(np.sin(y*0.2) * 4.0)
                    
                    if x < cliff_x - 4:
                        base = HIGH_H
                    elif x > cliff_x + 4:
                        base = LOW_H
                    else:
                        # The slope
                        t = (x - (cliff_x - 4)) / 8.0 # 0 to 1
                        base = int(HIGH_H * (1-t) + LOW_H * t)
                        is_cliff = True
                
                elif type == "hills":
                    base = LOW_H
                    # Broad rolling hills (Smooth)
                    # Sum of sines
                    n1 = (np.sin(x*0.1) + np.cos(y*0.1)) * 6.0
                    n2 = (np.sin(x*0.3 + 1.0) * np.sin(y*0.3 + 2.0)) * 2.0
                    
                    noise = (n1 + n2) * edge_mask
                    
                    # Shift up so we don't dig holes, just hills
                    if noise < 0: noise *= 0.2 # Flatten valleys
                    
                    base += int(noise)
                    # No cliff flag for gentle hills
                    
                elif type == "flat":
                    base = LOW_H
                    # Organic noise (Sum of Sines with rotation)
                    # Rotate coords slightly
                    xr = x * 0.9 - y * 0.4
                    yr = x * 0.4 + y * 0.9
                    
                    noise = (np.sin(xr*0.2) + np.cos(yr*0.25)) * 1.5
                    noise += np.sin(x*0.5 + y*0.5) * 0.5
                    
                    base += int(noise * edge_mask)
                
                elif type == "flat_var1":
                    base = LOW_H
                    # cellular-ish look
                    noise = (np.sin(x*0.4)*np.sin(y*0.4)) * 2.0
                    base += int(noise * edge_mask)

                elif type == "flat_var2":
                    base = LOW_H
                    # Diagonal noise
                    noise = np.sin((x+y)*0.4) * 1.5 * edge_mask
                    base += int(noise)
                
                # River Logic (Only for Low Ground)
                river_depth = 0
                is_river = False
                
                if "river" in type:
                    # Same river logic as before but relative to LOW_H
                    if type == "river_straight":
                        dist_x = abs(x - 32)
                        if dist_x < 14:
                            river_depth = max(0, 14 - dist_x) * 0.8
                            if river_depth > 6: river_depth = 6
                            is_river = True
                    elif type == "river_corner":
                        dx, dy = x - 64, y - 0
                        r_dist = np.sqrt(dx*dx + dy*dy)
                        dist_from_channel = abs(r_dist - 32)
                        if dist_from_channel < 14:
                            river_depth = max(0, 14 - dist_from_channel) * 0.8
                            if river_depth > 6: river_depth = 6
                            is_river = True
                
                final_h = int(base - river_depth)
                WATER_LEVEL = LOW_H - 2
                
                # Voxel Filling
                for z in range(H):
                    if z <= final_h:
                        if z == final_h and not is_river and not is_cliff:
                            # Grass
                            c = palette.LEAF_LIGHT if (x+y)%2 == 0 else palette.LEAF_BASE
                            voxels_grass.append([x - W//2, y - D//2, z])
                        elif z > final_h - 2 and not is_cliff:
                            # Soil
                            voxels_dirt.append([x - W//2, y - D//2, z])
                        else:
                            # Deep Dirt / Cliff Face
                            # Cliff face should be lighter dirt or stone?
                            # Let's use DIRT_BROWN (55)
                            voxels_dirt.append([x - W//2, y - D//2, z])
                    
                    if is_river and final_h < z <= WATER_LEVEL:
                        voxels_water.append([x - W//2, y - D//2, z])

        instr = []
        if voxels_dirt: instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": voxels_dirt, "color": palette.DIRT_BROWN})
        if voxels_grass: instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": voxels_grass, "color": palette.LEAF_LIGHT})
        if voxels_water: instr.append({"op": "add", "shape": "point_cloud", "pos": [0,0,0], "points": voxels_water, "color": palette.WATER_BLUE})
        
        with open(os.path.join(os.path.dirname(__file__), f"../csg/{name}.json"), "w") as f:
            json.dump({"name": name, "instructions": instr}, f)
            
    make_tile("tile_grass", "flat")
    make_tile("tile_grass_var1", "flat_var1")
    make_tile("tile_grass_var2", "flat_var2")
    make_tile("tile_grass_hills", "hills")
    make_tile("tile_plateau", "plateau")
    make_tile("tile_cliff_straight", "cliff_straight")
    make_tile("tile_river_straight", "river_straight")
    make_tile("tile_river_corner", "river_corner")
    print("Layered Tiles generated.")

if __name__ == "__main__":
    generate_tiles()
