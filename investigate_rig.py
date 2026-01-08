import json
import numpy as np

def check_bone(bone_name):
    with open('sprite_to_3d/actor_assets/hero/rig.json', 'r') as f:
        rig = json.load(f)
        
    bind_matrices = rig['skeleton']['bind_matrices']
    topology = rig['skeleton']['topology']
    
    # Calculate World Matrix from Bind Matrices (Row Major in JSON)
    def get_world(name):
        parent = topology.get(name)
        d = bind_matrices.get(name)
        if not d:
            local = np.identity(4)
        else:
            local = np.array(d).reshape(4, 4)
            
        if parent and parent != "root":
            return get_world(parent) @ local
        return local

    world_m = get_world(bone_name)
    print(f"World Matrix for {bone_name}:")
    print(world_m)
    
    # Check decomposition like in Lua (but correct for column major if needed)
    # If Lua code does:
    # m = mat4(d[1], d[5], d[9], d[13], ...)
    # then it's transposing d into m.
    # So m is the Column-Major version of d.
    
    # Let's see if the bone primary axis (Y in Mixamo) points towards the child.
    children = [k for k, v in topology.items() if v == bone_name]
    for child in children:
        child_world = get_world(child)
        direction = child_world[:3, 3] - world_m[:3, 3]
        length = np.linalg.norm(direction)
        direction /= length
        print(f"  Child {child} is at dist {length:.2f}, direction {direction}")
        
        # Local space direction
        local_dir = np.linalg.inv(world_m) @ np.append(child_world[:3, 3], 1.0)
        print(f"  Local dir to child: {local_dir[:3]}")

if __name__ == "__main__":
    check_bone('mixamorig_RightArm')
    check_bone('mixamorig_RightForeArm')
