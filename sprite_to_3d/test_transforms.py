import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sprite_to_3d.skeletons.mixamo import MixamoSkeleton

def get_world_matrix(bone_name):
    topology = MixamoSkeleton.TOPOLOGY
    bind_matrices = MixamoSkeleton.BIND_MATRICES
    # print(bind_matrices)
    
    chain = []
    curr = bone_name
    while curr is not None and curr != "root":
        chain.append(curr)
        curr = topology.get(curr)
    if curr == "root":
        chain.append("root")
    
    chain.reverse()
    
    world_m = np.identity(4)
    for b in chain:
        local_m_list = bind_matrices.get(b)
        if local_m_list:
            local_m = np.array(local_m_list).reshape(4, 4)
        else:
            # Fallback for 'root' or missing matrices
            local_m = np.identity(4)
            if b == 'mixamorig_Hips': # Hips has translation in get_t_pose
                 local_m[0:3, 3] = [0.0365, 28.4712, 0.3773]
        
        world_m = world_m @ local_m
        
    return world_m

def test_leg_connectivity():
    # Knee: mixamorig_RightLeg
    # Ankle: mixamorig_RightFoot
    knee_name = 'mixamorig_RightLeg'
    ankle_name = 'mixamorig_RightFoot'
    
    knee_world_m = get_world_matrix(knee_name)
    ankle_world_m = get_world_matrix(ankle_name)
    
    knee_pos = knee_world_m[:3, 3]
    ankle_pos = ankle_world_m[:3, 3]
    
    print(f"Knee World Pos: {knee_pos}")
    print(f"Ankle World Pos: {ankle_pos}")
    print(f"World Distance: {np.linalg.norm(ankle_pos - knee_pos):.4f}")
    
    # 1. Take a voxel at the Ankle world position
    v_world = np.append(ankle_pos, 1.0)
    
    # 2. Decompose into Knee-local space using Inverse World Matrix
    v_local = np.linalg.inv(knee_world_m) @ v_world
    print(f"\nAnkle position in Knee-local space: {v_local[:3]}")
    
    # DIAGNOSTIC: In Mixamo, local Y should be the primary axis of the leg
    # If the bone Y-axis points down the leg, v_local[1] should be positive and roughly 12.
    if abs(v_local[1]) > abs(v_local[0]) and abs(v_local[1]) > abs(v_local[2]):
        print(f"Confirmed: Local Y is the primary axis ({v_local[1]:.4f})")
    
    # 3. Reconstruct World Position
    v_reconstructed = (knee_world_m @ v_local)[:3]
    print(f"Reconstructed Ankle World Pos: {v_reconstructed}")
    
    error = np.linalg.norm(ankle_pos - v_reconstructed)
    print(f"Error: {error:.6f}")
    
    if error < 0.001:
        print("\nSUCCESS: Voxel at Ankle correctly follows Knee bone transformation.")
    else:
        print("\nFAILURE: Math error in transformation chain.")

if __name__ == "__main__":
    test_leg_connectivity()
