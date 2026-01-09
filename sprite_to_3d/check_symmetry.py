import numpy as np
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from skeletons.mixamo import MixamoSkeleton

def get_bone_length(bone_name):
    matrix = MixamoSkeleton.BIND_MATRICES.get(bone_name)
    if not matrix:
        return 0.0
    # Translation is at indices 3, 7, 11
    tx = matrix[3]
    ty = matrix[7]
    tz = matrix[11]
    return np.sqrt(tx**2 + ty**2 + tz**2)

def check_symmetry():
    bones = MixamoSkeleton.get_bones()
    left_bones = [b for b in bones if 'Left' in b]
    
    pose = MixamoSkeleton.get_t_pose(50)
    
    print(f"{'Bone Name':<30} | {'Len Diff':<10} | {'Pos Diff':<10} | {'Rot Diff':<10}")
    print("-" * 80)
    
    for l_bone in sorted(left_bones):
        r_bone = l_bone.replace('Left', 'Right')
        if r_bone in bones:
            l_m = np.array(MixamoSkeleton.BIND_MATRICES[l_bone]).reshape(4, 4)
            r_m = np.array(MixamoSkeleton.BIND_MATRICES[r_bone]).reshape(4, 4)
            
            l_len = np.linalg.norm(l_m[0:3, 3])
            r_len = np.linalg.norm(r_m[0:3, 3])
            diff_l = abs(l_len - r_len)
            
            lp = pose[l_bone]
            rp = pose[r_bone]
            # Flip X for right bone to compare world positions
            pos_diff = np.sqrt((lp[0] - (-rp[0]))**2 + (lp[1] - rp[1])**2 + (lp[2] - rp[2])**2)
            
            # Rotation symmetry: Mirror right rotation and compare to left
            # Mirrored R = M * R * M where M = diag(-1, 1, 1)
            # This is simplified: just checking Frobenius norm of difference
            l_rot = l_m[0:3, 0:3]
            r_rot = r_m[0:3, 0:3]
            
            # Mirroring a rotation matrix across X=0 plane
            # X basis becomes [-X, Y, Z]? No.
            # Standard mirroring of rotation:
            # [[r00, r01, r02],    [[ r00, -r01, -r02],
            #  [r10, r11, r12], ->  [-r10,  r11,  r12],
            #  [r20, r21, r22]]     [-r20,  r21,  r22]]
            # This depends on the convention. 
            
            # Let's just check if the diagonal elements are similar
            rot_diff = np.linalg.norm(l_rot - r_rot)
            
            print(f"{l_bone:<30} | {diff_l:<10.6f} | {pos_diff:<10.6f} | {rot_diff:<10.6f}")

if __name__ == "__main__":
    check_symmetry()
