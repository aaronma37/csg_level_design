import random

def create_brick_volume(start_pos, size, end_size=None, brick_size=(4, 2, 2), color=2, mortar=0, randomize_layout=False, taper_align=(0.5, 0.5), mortar_noise=0, noise_probability=0.05):
    """
    Generates a list of CSG 'add' instructions to fill a volume with a brick pattern.
    Assumes Z is UP.
    """
    instructions = []
    sx, sy, sz = start_pos
    w, d, h = size
    target_bw, target_bd, target_bh = brick_size
    align_x, align_y = taper_align
    
    tapering = end_size is not None
    if tapering:
        end_w, end_d = end_size
    else:
        end_w, end_d = w, d
    
    colors = color if isinstance(color, list) else [color]
    current_z = 0
    row_index = 0
    
    while current_z < h:
        layer_h = target_bh
        if randomize_layout:
             layer_h = random.randint(max(2, int(target_bh * 0.75)), int(target_bh * 1.25))
        actual_h = min(layer_h, h - current_z)
        if actual_h <= 0: break
        
        if tapering:
            progress = current_z / float(h)
            cur_layer_w = int(w + (end_w - w) * progress)
            cur_layer_d = int(d + (end_d - d) * progress)
            offset_x = int((w - cur_layer_w) * align_x)
            offset_y = int((d - cur_layer_d) * align_y)
        else:
            cur_layer_w = w
            cur_layer_d = d
            offset_x = 0
            offset_y = 0

        current_y = 0
        while current_y < cur_layer_d:
            layer_d = target_bd
            actual_d = min(layer_d, cur_layer_d - current_y)
            if actual_d <= 0: break
            
            current_x = 0
            if row_index % 2 == 1:
                current_x = -(target_bw // 2)
            
            if randomize_layout:
                current_x += random.randint(-2, 2)

            while current_x < cur_layer_w:
                this_brick_w = target_bw
                if randomize_layout:
                    this_brick_w = random.randint(max(2, int(target_bw * 0.5)), int(target_bw * 1.5))
                
                # Apply noise to brick boundaries
                dx_s, dx_e = 0, 0
                dy_s, dy_e = 0, 0
                dz_s, dz_e = 0, 0
                
                if mortar_noise > 0:
                    if random.random() < noise_probability:
                        dx_s = random.randint(-mortar_noise, mortar_noise)
                    if random.random() < noise_probability:
                        dx_e = random.randint(-mortar_noise, mortar_noise)
                    if random.random() < noise_probability:
                        dy_s = random.randint(-mortar_noise, mortar_noise)
                    if random.random() < noise_probability:
                        dy_e = random.randint(-mortar_noise, mortar_noise)
                    if random.random() < noise_probability:
                        dz_s = random.randint(-mortar_noise, mortar_noise)
                    if random.random() < noise_probability:
                        dz_e = random.randint(-mortar_noise, mortar_noise)

                real_x_start = max(0, current_x + dx_s)
                real_x_end = min(cur_layer_w, current_x + this_brick_w + dx_e)
                real_w = real_x_end - real_x_start
                
                # We need to handle Y and Z similarly but clamped to layer bounds
                real_y_start = max(0, current_y + dy_s)
                real_y_end = min(actual_d, actual_d + dy_e) # Relative to current_y
                # Wait, current_y is the loop var. actual_d is the size of this row.
                # The brick is at sy + offset_y + current_y.
                # So we modify the size relative to that.
                
                # Simplified: modify pos and size directly
                final_x = sx + offset_x + real_x_start
                final_y = sy + offset_y + current_y + dy_s
                final_z = sz + current_z + dz_s
                
                final_w = real_w
                final_d = actual_d + (dy_e - dy_s)
                final_h = actual_h + (dz_e - dz_s)

                if final_w > 0 and final_d > 0 and final_h > 0:
                     brick_color = random.choice(colors)
                     instructions.append({
                        "op": "add",
                        "pos": [final_x, final_y, final_z],
                        "size": [final_w, final_d, final_h],
                        "color": brick_color
                    })
                
                current_x += this_brick_w + mortar
            current_y += layer_d + mortar
        current_z += layer_h + mortar
    return instructions

def create_plank_volume(start_pos, size, plank_size=(24, 6, 2), color=4, mortar=0, direction='x'):
    """
    Generates a list of CSG 'add' instructions for floorboards.
    Assumes Z is UP.
    
    Args:
        start_pos: (x, y, z)
        size: (w, d, h)
        plank_size: (length, width, thickness)
        color: palette index OR list of palette indices
        mortar: gap between planks
        direction: 'x' or 'y' for plank orientation
    """
    instructions = []
    sx, sy, sz = start_pos
    w, d, h = size
    pl_len, pl_wid, pl_thk = plank_size
    colors = color if isinstance(color, list) else [color]

    current_z = 0
    while current_z < h:
        actual_h = min(pl_thk, h - current_z)
        
        if direction == 'x':
            # Planks run along X, they are wide along Y
            current_y = 0
            row_idx = 0
            while current_y < d:
                actual_wid = min(pl_wid, d - current_y)
                
                # Stagger X start
                current_x = 0
                if row_idx % 2 == 1:
                    current_x = -(pl_len // 2)
                
                while current_x < w:
                    # Variation in length
                    this_len = pl_len + random.randint(-4, 4)
                    
                    real_x_start = max(0, current_x)
                    real_x_end = min(w, current_x + this_len)
                    real_w = real_x_end - real_x_start
                    
                    if real_w > 0:
                        instructions.append({
                            "op": "add",
                            "pos": [sx + real_x_start, sy + current_y, sz + current_z],
                            "size": [real_w, actual_wid, actual_h],
                            "color": random.choice(colors)
                        })
                    current_x += this_len + mortar
                
                current_y += pl_wid + mortar
                row_idx += 1
        else:
            # Planks run along Y, wide along X
            current_x = 0
            row_idx = 0
            while current_x < w:
                actual_wid = min(pl_wid, w - current_x)
                
                current_y = 0
                if row_idx % 2 == 1:
                    current_y = -(pl_len // 2)
                
                while current_y < d:
                    this_len = pl_len + random.randint(-4, 4)
                    
                    real_y_start = max(0, current_y)
                    real_y_end = min(d, current_y + this_len)
                    real_d = real_y_end - real_y_start
                    
                    if real_d > 0:
                        instructions.append({
                            "op": "add",
                            "pos": [sx + current_x, sy + real_y_start, sz + current_z],
                            "size": [actual_wid, real_d, actual_h],
                            "color": random.choice(colors)
                        })
                    current_y += this_len + mortar
                current_x += pl_wid + mortar
                row_idx += 1
                
        current_z += pl_thk
    
    return instructions
