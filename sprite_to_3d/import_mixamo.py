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
    # Translation is in the last column (3, 7, 11 for Row-Major 4x4)
    # Scaled to voxel space (Mixamo is often in cm, we are ~50 units tall)
    # Mixamo Y is Up. Our Y is Up.
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

    for anim in animations:
        name = anim.get('name') or anim.get('id').replace("-anim", "")
        hero_bone = BONE_MAP.get(name)
        if not hero_bone: continue

        output_source = None
        for src in anim.findall("ns:source", ns):
            if 'Matrix-animation-output' in src.get('id', ''):
                output_source = src
                break
            
        if output_source is not None:
            float_array = output_source.find("ns:float_array", ns)
            data = [float(x) for x in float_array.text.split()]
            matrices = [data[i:i+16] for i in range(0, len(data), 16)]
            
            final_data = []
            for m in matrices:
                rot = extract_euler_from_matrix(m)
                pos = extract_pos_from_matrix(m) if hero_bone == "pelvis" else None
                
                rx, ry, rz = rot
                side, swing, twist = 0, 0, 0
                
                if "shoulder" in hero_bone or "elbow" in hero_bone or "hand" in hero_bone:
                    side_offset = -1.57 if "shoulder" in hero_bone else 0
                    if hero_bone not in RIGHT_SIDE:
                        side, swing, twist = side_offset, rx, ry
                    else:
                        side, swing, twist = -side_offset, -rx, -ry
                elif "hip" in hero_bone or "knee" in hero_bone or "foot" in hero_bone:
                    # Target 2 (X) is Bend for legs.
                    side, swing, twist = 0, 0, -rx
                    if "foot" in hero_bone: twist = -twist
                else:
                    # Pelvis/Torso
                    side, swing, twist = rz, rx, ry

                bone_frame = {"rot": [side, swing, twist]}
                if pos: bone_frame["pos"] = pos
                final_data.append(bone_frame)
                
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
    print(f"Converted {dae_path} -> {out_path} ({duration} frames)")

if __name__ == "__main__":
    convert_dae_to_json("sprite_to_3d/imports/Standard Walk.dae", "sprite_to_3d/preview_v2/hero_anim.json")
