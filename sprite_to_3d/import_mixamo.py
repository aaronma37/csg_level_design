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
    # Translation is in the last column
    # Scale: Mixamo is often ~100 units tall, we are 50. So 0.5 is correct.
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

    # First Pass: Find initial pelvis position for relative offset
    initial_pelvis_pos = None

    for anim in animations:
        name = anim.get('name') or anim.get('id').replace("-anim", "")
        hero_bone = BONE_MAP.get(name)
        if hero_bone == "pelvis":
            output_source = None
            for src in anim.findall("ns:source", ns):
                if 'Matrix-animation-output' in src.get('id', ''):
                    output_source = src
                    break
            if output_source is not None:
                float_array = output_source.find("ns:float_array", ns)
                data = [float(x) for x in float_array.text.split()]
                first_matrix = data[:16]
                initial_pelvis_pos = extract_pos_from_matrix(first_matrix)
            break

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
                pos = None
                if hero_bone == "pelvis":
                    raw_pos = extract_pos_from_matrix(m)
                    # Make it relative to the start of the animation
                    pos = [
                        raw_pos[0] - initial_pelvis_pos[0],
                        raw_pos[1] - initial_pelvis_pos[1],
                        raw_pos[2] - initial_pelvis_pos[2]
                    ]
                
                rx, ry, rz = rot
                side, swing, twist = 0, 0, 0
                
                if "shoulder" in hero_bone or "elbow" in hero_bone or "hand" in hero_bone:
                    # Arms (Along X)
                    side_offset = -1.57 if "shoulder" in hero_bone else 0
                    
                    if hero_bone not in RIGHT_SIDE:
                        # Left side (+X)
                        # side = Abduction (keep at offset to point down)
                        # swing = Flexion (walking swing)
                        # twist = Rotation
                        side = side_offset # Ignore rx if it pushes arms out
                        swing = -rx       # Use rx for swing
                        twist = ry
                    else:
                        # Right side (-X)
                        side = -side_offset 
                        swing = rx
                        twist = -ry
                elif "hip" in hero_bone or "knee" in hero_bone or "foot" in hero_bone:
                    # Legs (Along Y)
                    side, swing, twist = 0, 0, -rx
                    if "foot" in hero_bone: twist = -twist
                else:
                    # Torso
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