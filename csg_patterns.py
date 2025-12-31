import random

def create_brick_volume(start_pos, size, end_size=None, brick_size=(4, 2, 2), color=2, mortar=0, randomize_layout=False, taper_align=(0.5, 0.5)):
    """
    Generates a list of CSG 'add' instructions to fill a volume with a brick pattern.
    Assumes Z is UP.
    
    Args:
        start_pos: (x, y, z) tuple
        size: (w, d, h) tuple (Width X, Depth Y, Height Z)
        end_size: (w, d) tuple. If provided, width/depth linear interpolate to this at the top.
        brick_size: (bw, bd, bh) tuple (Target dimensions)
        color: palette index OR list of palette indices
        mortar: spacing between bricks (voxels of negative space)
        randomize_layout: If True, varies brick width and row height.
        taper_align: (x_align, y_align) tuple. 0.0=Start, 0.5=Center, 1.0=End.
                     Controls which side remains fixed during taper.
                     e.g. (0.5, 1.0) centers X taper, but aligns Y to the back (max Y).
    
    Returns:
        List of dicts (CSG instructions)
    """
    instructions = []
    sx, sy, sz = start_pos
    w, d, h = size
    target_bw, target_bd, target_bh = brick_size
    align_x, align_y = taper_align
    
    # Check if we are tapering
    tapering = end_size is not None
    if tapering:
        end_w, end_d = end_size
    else:
        end_w, end_d = w, d
    
    # Ensure color is a list
    colors = color if isinstance(color, list) else [color]
    
    current_z = 0
    row_index = 0
    
    while current_z < h:
        # Determine layer height
        layer_h = target_bh
        if randomize_layout:
             layer_h = random.randint(max(2, int(target_bh * 0.75)), int(target_bh * 1.25))
        
        # Clip height
        actual_h = min(layer_h, h - current_z)
        if actual_h <= 0: break
        
        # Calculate current layer dimensions (Linear Interpolation)
        if tapering:
            progress = current_z / float(h)
            cur_layer_w = int(w + (end_w - w) * progress)
            cur_layer_d = int(d + (end_d - d) * progress)
            
            # Alignment offset
            # if align=0.5 (center), offset = (diff)/2
            # if align=0.0 (start), offset = 0
            # if align=1.0 (end), offset = diff
            offset_x = int((w - cur_layer_w) * align_x)
            offset_y = int((d - cur_layer_d) * align_y)
        else:
            cur_layer_w = w
            cur_layer_d = d
            offset_x = 0
            offset_y = 0

        # Iterate Depth (Y)
        current_y = 0
        while current_y < cur_layer_d:
            layer_d = target_bd
            actual_d = min(layer_d, cur_layer_d - current_y)
            if actual_d <= 0: break
            
            # Iterate Width (X)
            current_x = 0
            # Bond pattern shift
            if row_index % 2 == 1:
                current_x = -(target_bw // 2)
            
            if randomize_layout:
                current_x += random.randint(-2, 2)

            while current_x < cur_layer_w:
                this_brick_w = target_bw
                if randomize_layout:
                    this_brick_w = random.randint(max(2, int(target_bw * 0.5)), int(target_bw * 1.5))
                
                real_x_start = max(0, current_x)
                real_x_end = min(cur_layer_w, current_x + this_brick_w)
                real_w = real_x_end - real_x_start
                
                if real_w > 0:
                     brick_color = random.choice(colors)
                     instructions.append({
                        "op": "add",
                        "pos": [sx + offset_x + real_x_start, sy + offset_y + current_y, sz + current_z],
                        "size": [real_w, actual_d, actual_h],
                        "color": brick_color
                    })
                
                current_x += this_brick_w + mortar
            
            current_y += layer_d + mortar
            
        current_z += layer_h + mortar
        row_index += 1

    return instructions