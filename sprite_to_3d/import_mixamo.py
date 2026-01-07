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

BONE_MAP = {
    "mixamorig_Hips": "pelvis",
    "mixamorig_Spine": "spine",
    "mixamorig_Neck": "neck",
    "mixamorig_Head": "head",
    "mixamorig_LeftArm": "shoulder_L",
    "mixamorig_RightArm": "shoulder_R",
    "mixamorig_LeftForeArm": "elbow_L",
    "mixamorig_RightForeArm": "elbow_R",
    "mixamorig_LeftHand": "hand_L",
    "mixamorig_RightHand": "hand_R",
    "mixamorig_LeftUpLeg": "hip_L",
    "mixamorig_RightUpLeg": "hip_R",
    "mixamorig_LeftLeg": "knee_L",
    "mixamorig_RightLeg": "knee_R",
    "mixamorig_LeftFoot": "foot_L",
    "mixamorig_RightFoot": "foot_R"
}

RIGHT_SIDE = {
    "shoulder_R", "elbow_R", "hand_R",
    "hip_R", "knee_R", "foot_R"
}

LEG_BONES = {
    "hip_L", "knee_L", "foot_L",
    "hip_R", "knee_R", "foot_R"
}

ARM_BONES = {
    "shoulder_L", "elbow_L", "hand_L",
    "shoulder_R", "elbow_R", "hand_R"
}

def convert_dae_to_json(dae_path, out_path):
    tree = ET.parse(dae_path)
    root = tree.getroot()
    ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}

    animations = root.findall('.//ns:library_animations/ns:animation', ns)
    
    extracted_anims = {}
    duration = 0

    for anim in animations:
        name = anim.get('name')
        if not name:
            name = anim.get('id').replace("-anim", "")
            
        hero_bone = BONE_MAP.get(name)
        if not hero_bone:
            continue

        output_source = None
        for src in anim.findall("ns:source", ns):
            src_id = src.get('id', '')
            if 'Matrix-animation-output-transform' in src_id or 'Matrix-animation-output' in src_id:
                output_source = src
                break
            
        if output_source is not None:
            float_array = output_source.find("ns:float_array", ns)
            data = [float(x) for x in float_array.text.split()]
            matrices = [data[i:i+16] for i in range(0, len(data), 16)]
            
            raw_eulers = [extract_euler_from_matrix(m) for m in matrices]
            final_eulers = []

            for e in raw_eulers:
                rx, ry, rz = e[0], e[1], e[2]
                
                if hero_bone in LEG_BONES:
                    # Legs: 
                    # Arg 1 (Side) = Static 180 + 0.1 (Abduct). Ignore 'rz' to stop Twist.
                    # Arg 2 (Twist) = 0.
                    # Arg 3 (Bend) = rx.
                    
                    final_rz = 0
                    final_rx = rx
                    final_ry = 0 # Twist 0
                    
                    # Fix Hips Pointing Up (Add 180 to Side/Arg 1)
                    # Removing PI offset as Rig Fix seems to have aligned it?
                    if hero_bone in ["hip_L", "hip_R"]:
                        pass
                        # final_rz += math.pi
                        
                    if hero_bone in LEG_BONES:
                        final_rz += 0.1 # Abduct
                        
                    new_e = [final_rz, final_ry, final_rx]
                    
                elif hero_bone in ARM_BONES:
                    # Arms: Map [rz, rx, ry]
                    # Rig is Straight Down (Fixed).
                    # But Mixamo Data is relative to T-Pose (Horizontal).
                    # So we MUST offset by -1.57 to bring animation to Down space?
                    # Wait. If Rig is Down. And Mixamo is 0 (Horizontal).
                    # If we apply 0, Rig stays Down?
                    # User said "Stick out 90". So Mixamo 0 maps to 90 offset?
                    # This implies Menori/Rig T-Pose is 0. And Fixed Rig is T-Pose?
                    # No, I moved bones.
                    
                    # Arms: Map [rz, rx, ry]
                    # Arg 1 (Z) = Side (rz)
                    # Arg 2 (Y) = Swing (rx) -> Arg 2 is Swing.
                    # Arg 3 (X) = Twist (0) -> Arg 3 is Twist.
                    
                    final_rz = -1.57 # Down
                    
                    offset_rx = rx
                    if hero_bone in RIGHT_SIDE:
                        offset_rx *= -2
                    else:
                        offset_rx *= 2
                    
                    # Map to [Side, Swing, Twist] -> [rz, rx, 0]
                    new_e = [final_rz, offset_rx, 0]
                    # new_e = [final_rz, offset_rx, 0]
                    
                else:
                    # Torso
                    new_e = [rz, rx, ry]

                if hero_bone in RIGHT_SIDE:
                    if hero_bone in LEG_BONES:
                        # Legs: Invert Side (0), Twist (1). KEEP Bend (2).
                        new_e = [-new_e[0], -new_e[1], new_e[2]]
                    elif hero_bone in ARM_BONES:
                        # Arms: Invert Side (0), Twist (2). KEEP Swing (1).
                        new_e = [-new_e[0], new_e[1], -new_e[2]]
                    else:
                        new_e = [-new_e[0], -new_e[1], -new_e[2]]
                    
                final_eulers.append(new_e)
                
            extracted_anims[hero_bone] = final_eulers
            duration = max(duration, len(final_eulers))

    frames = []
    for i in range(duration):
        frame = {}
        for bone, eulers in extracted_anims.items():
            if i < len(eulers):
                frame[bone] = eulers[i]
        frames.append(frame)

    output = {
        "duration": duration,
        "frames": frames
    }

    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Converted {dae_path} -> {out_path} ({duration} frames)")

if __name__ == "__main__":
    dae_file = "sprite_to_3d/imports/Standard Walk.dae"
    out_file = "sprite_to_3d/preview_v2/hero_anim.json"
    convert_dae_to_json(dae_file, out_file)
