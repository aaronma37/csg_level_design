import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'sprite_to_3d')))
from skeletons.mixamo import MixamoSkeleton

def check():
    topology = MixamoSkeleton.TOPOLOGY
    bind_matrices = MixamoSkeleton.BIND_MATRICES
    t_pose = MixamoSkeleton.get_t_pose(50.0) # Height 50
    
    bones = list(topology.keys())
    ordered_bones = []
    visited = set()
    while len(ordered_bones) < len(bones):
        for b in bones:
            if b in visited: continue
            parent = topology[b]
            if parent is None or parent == "root" or parent in visited:
                ordered_bones.append(b)
                visited.add(b)
                
    world_matrices = {}
    for bone in ordered_bones:
        parent = topology[bone]
        if parent == "root": parent = None
        
        bind_m = bind_matrices.get(bone)
        if bind_m:
            local_m = np.array(bind_m).reshape(4, 4)
        else:
            local_m = np.identity(4)
            if bone == 'mixamorig_Hips':
                local_m[0:3, 3] = t_pose['mixamorig_Hips']
        
        if parent is None:
            world_matrices[bone] = local_m
        else:
            world_matrices[bone] = world_matrices[parent] @ local_m
            
        # Check position
        calc_pos = world_matrices[bone][:3, 3]
        actual_pos = np.array(t_pose.get(bone, (0,0,0)))
        
        dist = np.linalg.norm(calc_pos - actual_pos)
        if dist > 0.1:
            print(f"MISMATCH: {bone}")
            print(f"  Calc: {calc_pos}")
            print(f"  Pose: {actual_pos}")
            print(f"  Dist: {dist:.4f}")
        else:
            print(f"MATCH: {bone} (Dist: {dist:.4f})")

if __name__ == "__main__":
    check()
