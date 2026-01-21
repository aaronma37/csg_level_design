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
        # Batch points by palette index
        points_by_color = {} # color_idx -> list of [x, y, z]

        def add_point(x, y, z, color_idx):
            if color_idx not in points_by_color:
                points_by_color[color_idx] = []
            points_by_color[color_idx].append([x - W//2, y - D//2, z])
        
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
                    noise = int(np.sin(x*0.4) * np.cos(y*0.4) * 1.5 * edge_mask)
                    base += noise
                    
                elif type == "cliff_straight":
                    cliff_x = 32 + int(np.sin(y*0.2) * 4.0)
                    if x < cliff_x - 4: base = HIGH_H
                    elif x > cliff_x + 4: base = LOW_H
                    else:
                        t = (x - (cliff_x - 4)) / 8.0 
                        base = int(HIGH_H * (1-t) + LOW_H * t)
                        is_cliff = True
                
                elif type == "hills":
                    base = LOW_H
                    n1 = (np.sin(x*0.1) + np.cos(y*0.1)) * 6.0
                    n2 = (np.sin(x*0.3 + 1.0) * np.sin(y*0.3 + 2.0)) * 2.0
                    noise = (n1 + n2) * edge_mask
                    if noise < 0: noise *= 0.2
                    base += int(noise)
                    
                elif type == "flat":
                    base = LOW_H
                    xr = x * 0.9 - y * 0.4
                    yr = x * 0.4 + y * 0.9
                    noise = (np.sin(xr*0.2) + np.cos(yr*0.25)) * 1.5
                    noise += np.sin(x*0.5 + y*0.5) * 0.5
                    base += int(noise * edge_mask)
                
                elif type == "flat_var1":
                    base = LOW_H
                    noise = (np.sin(x*0.4)*np.sin(y*0.4)) * 2.0
                    base += int(noise * edge_mask)

                elif type == "flat_var2":
                    base = LOW_H
                    noise = np.sin((x+y)*0.4) * 1.5 * edge_mask
                    base += int(noise)
                
                # River Logic
                river_depth = 0
                is_river = False
                dist_to_bank = 0
                
                if "river" in type:
                    if type == "river_straight":
                        dist_x = abs(x - 32)
                        dist_to_bank = 14 - dist_x
                        if dist_x < 14:
                            river_depth = max(0, dist_to_bank) * 0.8
                            if river_depth > 6: river_depth = 6
                            is_river = True
                    elif type == "river_corner":
                        dx, dy = x - 64, y - 0
                        r_dist = np.sqrt(dx*dx + dy*dy)
                        dist_from_channel = abs(r_dist - 32)
                        dist_to_bank = 14 - dist_from_channel
                        if dist_from_channel < 14:
                            river_depth = max(0, dist_to_bank) * 0.8
                            if river_depth > 6: river_depth = 6
                            is_river = True
                
                final_h = int(base - river_depth)
                WATER_LEVEL = LOW_H - 2
                
                # Voxel Filling
                for z in range(H):
                    if z <= final_h:
                        if z == final_h and not is_river and not is_cliff:
                            # Grass (Use GRASS_RANGE 60-69)
                            # Noise based selection
                            noise_val = np.sin(x*0.3) * np.cos(y*0.3) * 5 + 5 # 0 to 10
                            idx_offset = int(noise_val) % 10
                            
                            # Add high-frequency noise for texture
                            if (x+y)%3 == 0: idx_offset = (idx_offset + 2) % 10
                            
                            grass_col = palette.GRASS_RANGE[idx_offset]
                            add_point(x, y, z, grass_col)
                            
                        elif z > final_h - 2 and not is_cliff:
                            add_point(x, y, z, palette.DIRT_BROWN)
                        else:
                            add_point(x, y, z, palette.DIRT_BROWN)
                    
                    if is_river and final_h < z <= WATER_LEVEL:
                        # Water (Use WATER_RANGE 70-79)
                        # Depth gradient: Deeper = Lower Index
                        depth_from_surface = WATER_LEVEL - z
                        water_idx_offset = max(0, min(9, 9 - depth_from_surface * 3))
                        
                        # Foam at edges (where river_depth is shallow)
                        if z == WATER_LEVEL and dist_to_bank < 3:
                            water_idx_offset = 9 # Foam
                            
                        water_col = palette.WATER_RANGE[water_idx_offset]
                        add_point(x, y, z, water_col)

        instr = []
        for color_idx, points in points_by_color.items():
            instr.append({
                "op": "add", 
                "shape": "point_cloud", 
                "pos": [0,0,0], 
                "points": points, 
                "color": color_idx
            })
        
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
