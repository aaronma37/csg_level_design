import numpy as np
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from skeletons.mixamo import MixamoSkeleton

def get_bone_length(bone_name):
    matrix = MixamoSkeleton.BIND_MATRICES.get(bone_name)
    if not matrix: return 0.0
    tx, ty, tz = matrix[3], matrix[7], matrix[11]
    return np.sqrt(tx**2 + ty**2 + tz**2)

def test_legs():
    pose = MixamoSkeleton.get_t_pose(50)
    
    # Left Leg Chain
    l_up = "mixamorig_LeftUpLeg"
    l_leg = "mixamorig_LeftLeg"
    l_foot = "mixamorig_LeftFoot"
    
    # Right Leg Chain
    r_up = "mixamorig_RightUpLeg"
    r_leg = "mixamorig_RightLeg"
    r_foot = "mixamorig_RightFoot"
    
    # 1. Bone Lengths (Local)
    l_len = get_bone_length(l_leg) + get_bone_length(l_foot)
    r_len = get_bone_length(r_leg) + get_bone_length(r_foot)
    
    print(f"--- Bone Lengths (Sum of local translations) ---")
    print(f"Left Leg Length:  {l_len:.6f}")
    print(f"Right Leg Length: {r_len:.6f}")
    print(f"Diff:             {abs(l_len - r_len):.6f}")
    
    # 2. Vertical Reach (Y difference in world pose)
    l_hips_y = pose["mixamorig_Hips"][1]
    l_foot_y = pose[l_foot][1]
    l_reach = l_hips_y - l_foot_y
    
    r_hips_y = pose["mixamorig_Hips"][1]
    r_foot_y = pose[r_foot][1]
    r_reach = r_hips_y - r_foot_y
    
    print(f"\n--- Vertical Reach (Hips Y - Foot Y) ---")
    print(f"Left Reach:  {l_reach:.6f}")
    print(f"Right Reach: {r_reach:.6f}")
    print(f"Diff:        {abs(l_reach - r_reach):.6f}")
    
    # 3. Straight Line Distance (World)
    l_dist = np.sqrt(sum((a-b)**2 for a, b in zip(pose["mixamorig_Hips"], pose[l_foot])))
    r_dist = np.sqrt(sum((a-b)**2 for a, b in zip(pose["mixamorig_Hips"], pose[r_foot])))
    
    print(f"\n--- Straight Line Distance (Hips to Foot) ---")
    print(f"Left Dist:   {l_dist:.6f}")
    print(f"Right Dist:  {r_dist:.6f}")
    print(f"Diff:        {abs(l_dist - r_dist):.6f}")

if __name__ == "__main__":
    test_legs()
