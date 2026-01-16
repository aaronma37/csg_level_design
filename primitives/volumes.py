import math

def get_cuboid_voxels(x, y, z, dx, dy, dz):
    voxels = []
    for i in range(int(dx)):
        for j in range(int(dy)):
            for k in range(int(dz)):
                voxels.append((int(x + i), int(y + j), int(z + k)))
    return voxels

def get_sphere_voxels(cx, cy, cz, radius):
    voxels = []
    r_int = int(math.ceil(radius))
    r2 = radius * radius
    for dz in range(-r_int, r_int + 1):
        for dy in range(-r_int, r_int + 1):
            for dx in range(-r_int, r_int + 1):
                if dx*dx + dy*dy + dz*dz <= r2:
                    voxels.append((int(cx + dx), int(cy + dy), int(cz + dz)))
    return voxels

def get_cylinder_voxels(cx, cy, cz, radius, height, axis='z'):
    voxels = []
    r_int = int(math.ceil(radius))
    r2 = radius * radius
    h_int = int(height)
    
    for h in range(h_int):
        for da in range(-r_int, r_int + 1):
            for db in range(-r_int, r_int + 1):
                if da*da + db*db <= r2:
                    if axis == 'z':
                        voxels.append((int(cx + da), int(cy + db), int(cz + h)))
                    elif axis == 'y':
                        voxels.append((int(cx + da), int(cy + h), int(cz + db)))
                    else: # axis == 'x'
                        voxels.append((int(cx + h), int(cy + da), int(cz + db)))
    return voxels

def get_cone_voxels(cx, cy, cz, radius_bottom, radius_top, height, axis='z'):
    voxels = []
    h_int = int(height)
    
    for h in range(h_int):
        progress = h / float(height) if height > 0 else 0
        r = radius_bottom + (radius_top - radius_bottom) * progress
        r_int = int(math.ceil(r))
        r2 = r * r
        for da in range(-r_int, r_int + 1):
            for db in range(-r_int, r_int + 1):
                if da*da + db*db <= r2:
                    if axis == 'z':
                        voxels.append((int(cx + da), int(cy + db), int(cz + h)))
                    elif axis == 'y':
                        voxels.append((int(cx + da), int(cy + h), int(cz + db)))
                    else: # axis == 'x'
                        voxels.append((int(cx + h), int(cy + da), int(cz + db)))
    return voxels

def get_ellipsoid_voxels(cx, cy, cz, rx, ry, rz):
    voxels = []
    # Bounding box
    idx, idy, idz = int(math.ceil(rx)), int(math.ceil(ry)), int(math.ceil(rz))
    
    for dz in range(-idz, idz + 1):
        for dy in range(-idy, idy + 1):
            for dx in range(-idx, idx + 1):
                # Ellipsoid equation: x^2/a^2 + y^2/b^2 + z^2/c^2 <= 1
                if (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) + (dz*dz)/(rz*rz) <= 1.0:
                    voxels.append((int(cx + dx), int(cy + dy), int(cz + dz)))
    return voxels
