import xml.etree.ElementTree as ET
import json
import numpy as np
import math
import sys
import os

def extract_euler_from_matrix(m):
    # DAE matrices are 4x4, Row-Major
    r11, r12, r13 = m[0], m[1], m[2]
    r21, r22, r23 = m[4], m[5], m[6]
    r31, r32, r33 = m[8], m[9], m[10]

    if r31 < 1:
        if r31 > -1:
            y = math.asin(-r31)
            x = math.atan2(r32, r33)
            z = math.atan2(r21, r11)
        else: # r31 = -1
            y = math.pi/2
            x = -math.atan2(-r23, r22)
            z = 0
    else: # r31 = 1
        y = -math.pi/2
        x = math.atan2(-r23, r22)
        z = 0
        
    return [x, y, z]

def extract_pos_from_matrix(m):
    return [m[3] * 0.5, m[7] * 0.5, m[11] * 0.5]

BONE_MAP = {
    "mixamorig_Hips": "pelvis",
    "mixamorig_Spine": "spine",
    "mixamorig_Neck": "neck",
    "mixamorig_Head": "head",
    "mixamorig_LeftArm": "shoulder_R",
    "mixamorig_RightArm": "shoulder_L",
    "mixamorig_LeftForeArm": "elbow_R",
    "mixamorig_RightForeArm": "elbow_L",
    "mixamorig_LeftHand": "hand_R",
    "mixamorig_RightHand": "hand_L",
    "mixamorig_LeftUpLeg": "hip_R",
    "mixamorig_RightUpLeg": "hip_L",
    "mixamorig_LeftLeg": "knee_R",
    "mixamorig_RightLeg": "knee_L",
    "mixamorig_LeftFoot": "foot_R",
    "mixamorig_RightFoot": "foot_L"
}

RIGHT_SIDE = {"shoulder_R", "elbow_R", "hand_R", "hip_R", "knee_R", "foot_R"}

def convert_dae_to_json(dae_path, out_path):
    tree = ET.parse(dae_path)
    root = tree.getroot()
    ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}

    animations = root.findall('.//ns:library_animations/ns:animation', ns)
    extracted_anims = {}
    duration = 0

    initial_pelvis_pos = None
    for anim in animations:
        name = anim.get('name') or anim.get('id').replace("-anim", "")
        if BONE_MAP.get(name) == "pelvis":
            src = None
            for s in anim.findall("ns:source", ns):
                if 'Matrix-animation-output' in s.get('id', ''):
                    src = s
                    break
            if src is not None:
                fa = src.find("ns:float_array", ns)
                d = [float(x) for x in fa.text.split()]
                initial_pelvis_pos = extract_pos_from_matrix(d[:16])
            break

    for anim in animations:
        name = anim.get('name') or anim.get('id').replace("-anim", "")
        hero_bone = BONE_MAP.get(name)
        if not hero_bone: continue

        src = None
        for s in anim.findall("ns:source", ns):
            if 'Matrix-animation-output' in s.get('id', ''):
                src = s
                break
            
        if src is not None:
            float_array = src.find("ns:float_array", ns)
            data = [float(x) for x in float_array.text.split()]
            matrices = [data[i:i+16] for i in range(0, len(data), 16)]
            raw_data = [extract_euler_from_matrix(m) for m in matrices]
            
            # Centering averages
            avgs = [sum(r[j] for r in raw_data)/len(matrices) for j in range(3)]

            # Step 1: Calculate Variance for each axis
            variances = [0, 0, 0]
            if len(raw_data) > 1:
                for j in range(3):
                    c_avg = avgs[j]
                    variances[j] = sum((r[j] - c_avg)**2 for r in raw_data) / len(raw_data)
            
            # Step 2: Auto-select the swing value from the best variance axis
            best_axis_idx = variances.index(max(variances))
            
            final_data = []
            for i, rot in enumerate(raw_data):
                m = matrices[i]
                pos = extract_pos_from_matrix(m) if hero_bone == "pelvis" else None
                
                # Centered versions of all three channels
                crots = [rot[j] - avgs[j] for j in range(3)]
                best_swing = crots[best_axis_idx]
                
                side, swing, twist = 0, 0, 0
                
                if "shoulder" in hero_bone or "elbow" in hero_bone or "hand" in hero_bone:
                    base_side = -1.57 if "shoulder" in hero_bone else 0
                    if hero_bone not in RIGHT_SIDE:
                        side, swing, twist = base_side, best_swing, 0
                    else:
                        side = -base_side
                        # Use best_swing directly. Mixamo already handled the phase/timing.
                        swing = best_swing
                        twist = 0
                
                elif "hip" in hero_bone or "knee" in hero_bone or "foot" in hero_bone:
                    # Leg Bend (Target 2/Twist)
                    val = -crots[0]
                    
                    side, swing, twist = 0, 0, val
                    if "foot" in hero_bone: twist = -twist
                    if hero_bone in RIGHT_SIDE:
                        twist = twist 
                else:
                    # Torso/Hips
                    crx, cry, crz = crots
                    side, swing, twist = crz, crx, cry

                bf = {"rot": [side, swing, twist]}
                if pos and initial_pelvis_pos:
                    bf["pos"] = [pos[0]-initial_pelvis_pos[0], pos[1]-initial_pelvis_pos[1], pos[2]-initial_pelvis_pos[2]]
                final_data.append(bf)
            
            extracted_anims[hero_bone] = final_data
            duration = max(duration, len(final_data))

    frames = []
    for i in range(duration):
        frame = {}
        for bone, data in extracted_anims.items():
            if i < len(data): frame[bone] = data[i]
        frames.append(frame)

    with open(out_path, 'w') as f:
        json.dump({"duration": duration, "frames": frames}, f, indent=2)
    print(f"Variance Step 1 Complete: Converted {dae_path}")

if __name__ == "__main__":
    convert_dae_to_json("sprite_to_3d/imports/Standard Walk.dae", "sprite_to_3d/preview_v2/hero_anim.json")