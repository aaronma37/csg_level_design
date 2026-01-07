import json
import math

OFFSETS = {
    # Child -> Parent : Offset (Child Local Pos in Parent Space)
    "knee_L": ("hip_L", [2.0, -10.0, 0.0]),
    "foot_L": ("knee_L", [2.0, -11.0, 0.0]),
    "knee_R": ("hip_R", [-2.0, -10.0, 0.0]),
    "foot_R": ("knee_R", [-2.0, -11.0, 0.0]),
    "elbow_L": ("shoulder_L", [7.0, 0.0, 0.0]),
    "hand_L": ("elbow_L", [6.0, 0.0, 0.0]),
    "elbow_R": ("shoulder_R", [-7.0, 0.0, 0.0]),
    "hand_R": ("elbow_R", [-6.0, 0.0, 0.0]),
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
    # Move voxels from child bones to parent bones if they are physically located there.
    
    # Define Move pairs
    MOVES = [
        ("knee_L", "hip_L"), ("foot_L", "knee_L"),
        ("knee_R", "hip_R"), ("foot_R", "knee_R"),
        ("elbow_L", "shoulder_L"), ("hand_L", "elbow_L"),
        ("elbow_R", "shoulder_R"), ("hand_R", "elbow_R")
    ]
    
    for child, parent in MOVES:
        if child in parts and len(parts[child]['voxels']) > 0:
            offset = OFFSETS[child][1]
            # Heuristic: If part has significant volume, move it.
            # (Legs use Y threshold, Arms use X threshold? No, just move all for now
            # except Foot/Hand which we might want to split).
            
            # For Arms, move all.
            if "elbow" in child:
                print(f"Moving Upper Arm from {child} to {parent}")
                move_all = True
            elif "hand" in child:
                print(f"Moving Forearm from {child} to {parent}")
                move_all = True
            elif "knee" in child:
                # Check for Thigh (Y > 5 in knee space)
                ys = [v[1] for v in parts[child]['voxels']]
                move_all = max(ys) > 5.0
            else:
                move_all = False
                
            if move_all:
                voxels = parts[child]['voxels']
                transformed = []
                for v in voxels:
                    nx = v[0] + offset[0]
                    ny = v[1] + offset[1]
                    nz = v[2] + offset[2]
                    transformed.append([nx, ny, nz, v[3]])
                
                if parent not in parts: parts[parent] = {'voxels': []}
                parts[parent]['voxels'].extend(transformed)
                parts[child]['voxels'] = []

    # Foot/Hand special split logic
    for side in ["_L", "_R"]:
        for joint, parent, axis_idx, threshold in [("foot"+side, "knee"+side, 1, 2.0), ("hand"+side, "elbow"+side, 0, 2.0)]:
            if joint in parts and len(parts[joint]['voxels']) > 0:
                # For hands, if it's Right side, threshold might be negative?
                # hand_R: X-range -1 to 7. Pivot 0.
                # hand_L: X-range -7 to 1. Pivot 0.
                # Let's just move everything for hands/feet if they haven't been moved yet.
                pass



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

    # --- PHASE 3: Straighten Arms (Rotate Voxels -90/+90 Z) ---
    # Left: (X+, Y0) -> (X0, Y-) => Rotate -90 (CW)
    # Right: (X-, Y0) -> (X0, Y-) => Rotate +90 (CCW)
    
    arm_angle = math.pi / 2.0
    
    for side, sign in [("_L", -1), ("_R", 1)]:
        shoulder = "shoulder" + side
        elbow = "elbow" + side
        hand = "hand" + side
        
        # Check if already straight (Elbow X == Shoulder X)
        if shoulder in skel and elbow in skel:
            sp = skel[shoulder]
            ep = skel[elbow]
            if abs(ep[0] - sp[0]) > 0.1: # Angled
                print(f"Straightening {side} arm...")
                rot_angle = sign * arm_angle
                
                # Rotate Upper Arm (in Shoulder)
                if shoulder in parts:
                    new_v = []
                    for v in parts[shoulder]['voxels']:
                        rx, ry = rotate_z(v[0], v[1], rot_angle)
                        new_v.append([rx, ry, v[2], v[3]])
                    parts[shoulder]['voxels'] = new_v
                    
                # Rotate Forearm (in Elbow)
                if elbow in parts:
                    new_v = []
                    for v in parts[elbow]['voxels']:
                        rx, ry = rotate_z(v[0], v[1], rot_angle)
                        new_v.append([rx, ry, v[2], v[3]])
                    parts[elbow]['voxels'] = new_v
                    
                # Update Elbow Pos
                dx = sp[0] - ep[0]
                dy = sp[1] - ep[1]
                length = math.sqrt(dx*dx + dy*dy)
                skel[elbow] = [sp[0], sp[1] - length, ep[2]]
                
                # Update Hand Pos
                if hand in skel:
                    hp = skel[hand]
                    dxe = ep[0] - hp[0]
                    dye = ep[1] - hp[1]
                    hlen = math.sqrt(dxe*dxe + dye*dye)
                    ne = skel[elbow]
                    skel[hand] = [ne[0], ne[1] - hlen, hp[2]]

    with open(path, 'w') as f:
        json.dump(data, f)
    print("Fixed Rig Hierarchy AND Straightened Legs AND Arms")