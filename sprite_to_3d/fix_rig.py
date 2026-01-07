import json
import math

OFFSETS = {
    # Child -> Parent : Offset (Child Local Pos in Parent Space)
    "knee_L": ("hip_L", [2.0, -10.0, 0.0]),
    "foot_L": ("knee_L", [2.0, -11.0, 0.0]),
    "knee_R": ("hip_R", [-2.0, -10.0, 0.0]),
    "foot_R": ("knee_R", [-2.0, -11.0, 0.0]),
}

def rotate_z(x, y, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return x*c - y*s, x*s + y*c

def fix():
    print("Starting Fix Rig...")
    path = 'sprite_to_3d/preview_v2/hero_rigged.json'
    with open(path) as f:
        data = json.load(f)
        
    parts = data['parts']
    skel = data['skeleton']['rest_pose']
    
    # --- PHASE 0: Repair Broken Hierarchy ---
    for side in ["_L", "_R"]:
        hip = "hip" + side
        knee = "knee" + side
        offset = OFFSETS[knee][1]
        
        if hip in parts and knee in parts:
            if len(parts[knee]['voxels']) == 0 and len(parts[hip]['voxels']) > 50:
                ys = [v[1] for v in parts[hip]['voxels']]
                if min(ys) < -8.0:
                    print(f"Repairing {side} hierarchy (Shin in Hip detected)...")
                    hip_voxels = parts[hip]['voxels']
                    thigh_voxels = []
                    shin_voxels = []
                    for v in hip_voxels:
                        if v[1] < -5.0:
                            nx = v[0] - offset[0]
                            ny = v[1] - offset[1]
                            nz = v[2] - offset[2]
                            shin_voxels.append([nx, ny, nz, v[3]])
                        else:
                            thigh_voxels.append(v)
                    parts[hip]['voxels'] = thigh_voxels
                    parts[knee]['voxels'] = shin_voxels

    # --- PHASE 1: Fix Hierarchy (Shift Up) ---
    for side in ["_L", "_R"]:
        knee = "knee" + side
        hip = "hip" + side
        offset = OFFSETS[knee][1] 
        
        if knee in parts and len(parts[knee]['voxels']) > 0:
            ys = [v[1] for v in parts[knee]['voxels']]
            if max(ys) > 5.0:
                print(f"Moving Thigh from {knee} to {hip}")
                knee_voxels = parts[knee]['voxels']
                transformed_voxels = []
                for v in knee_voxels:
                    nx = v[0] + offset[0]
                    ny = v[1] + offset[1]
                    nz = v[2] + offset[2]
                    transformed_voxels.append([nx, ny, nz, v[3]])
                
                if hip not in parts: parts[hip] = {'voxels': []}
                parts[hip]['voxels'].extend(transformed_voxels)
                parts[knee]['voxels'] = []
            
    for side in ["_L", "_R"]:
        foot = "foot" + side
        knee = "knee" + side
        offset = OFFSETS[foot][1]
        
        if foot in parts and len(parts[foot]['voxels']) > 0:
            ys = [v[1] for v in parts[foot]['voxels']]
            if max(ys) > 5.0:
                print(f"Moving Shin from {foot} to {knee}")
                foot_voxels = parts[foot]['voxels']
                shin_voxels = []
                foot_kept = []
                for v in foot_voxels:
                    if v[1] > 2.0:
                        nx = v[0] + offset[0]
                        ny = v[1] + offset[1]
                        nz = v[2] + offset[2]
                        shin_voxels.append([nx, ny, nz, v[3]])
                    else:
                        foot_kept.append(v)
                
                if knee not in parts: parts[knee] = {'voxels': []}
                parts[knee]['voxels'].extend(shin_voxels)
                parts[foot]['voxels'] = foot_kept

    # --- PHASE 2: Straighten Legs ---
    angle = math.atan2(2.0, 10.0)
    
    for side, sign in [("_L", -1), ("_R", 1)]:
        hip = "hip" + side
        knee = "knee" + side
        foot = "foot" + side
        
        if hip in skel and knee in skel:
            hp = skel[hip]
            kp = skel[knee]
            if abs(kp[0] - hp[0]) > 0.1:
                print(f"Straightening {side} leg...")
                rot_angle = sign * angle
                
                if hip in parts:
                    new_v = []
                    for v in parts[hip]['voxels']:
                        rx, ry = rotate_z(v[0], v[1], rot_angle)
                        new_v.append([rx, ry, v[2], v[3]])
                    parts[hip]['voxels'] = new_v
                    
                if knee in parts:
                    new_v = []
                    for v in parts[knee]['voxels']:
                        rx, ry = rotate_z(v[0], v[1], rot_angle)
                        new_v.append([rx, ry, v[2], v[3]])
                    parts[knee]['voxels'] = new_v
                    
                dy = hp[1] - kp[1]
                dx = hp[0] - kp[0]
                length = math.sqrt(dx*dx + dy*dy)
                skel[knee] = [hp[0], hp[1] - length, kp[2]]
                
                if foot in skel:
                    fp = skel[foot]
                    dyf = kp[1] - fp[1]
                    dxf = kp[0] - fp[0]
                    flen = math.sqrt(dxf*dxf + dyf*dyf)
                    nk = skel[knee]
                    skel[foot] = [nk[0], nk[1] - flen, fp[2]]

    with open(path, 'w') as f:
        json.dump(data, f)
    print("Fixed Rig Hierarchy AND Straightened Legs")

if __name__ == "__main__":
    fix()