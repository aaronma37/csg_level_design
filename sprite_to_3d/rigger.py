import json
import math
import os
import sys
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class VoxelRigger:
    def __init__(self, generator):
        self.generator = generator
        self.voxels = generator.builder.voxels
        self.owners = generator.voxel_owners
        self.pose = generator.pose
        self.topology = generator.blueprint['topology']
        
        # Pre-calculate world matrices for the rest pose
        self.world_matrices = self._calculate_world_matrices()
        
    def _calculate_world_matrices(self):
        matrices = {}
        bones = list(self.topology.keys())
        bone_scales = self.generator.bone_scales
        
        # Parent-first ordering
        ordered_bones = []
        visited = set()
        while len(ordered_bones) < len(bones):
            for b in bones:
                if b in visited: continue
                parent = self.topology[b]
                if parent is None or parent == "root" or parent in visited:
                    ordered_bones.append(b)
                    visited.add(b)

        has_bind = hasattr(self.generator.skeleton_class, "BIND_MATRICES")
        
        # Identity for root
        matrices['root'] = np.identity(4)

        for bone in ordered_bones:
            if bone == 'root': continue
            parent = self.topology[bone]
            if parent == "root": parent = 'root'
            
            # 1. Get Local Scale
            s = bone_scales.get(bone, [1.0, 1.0, 1.0])
            scale_m = np.diag([s[0], s[1], s[2], 1.0])
            
            if has_bind:
                bind_m = self.generator.skeleton_class.BIND_MATRICES.get(bone)
                if bind_m:
                    m_data = list(bind_m[:16])
                    while len(m_data) < 16:
                        if len(m_data) == 15:
                            m_data.append(1.0)
                        else:
                            m_data.append(0.0)
                    local_m = np.array(m_data).reshape(4, 4)
                    
                    # Parent info
                    p_mat = matrices.get(parent, np.identity(4))
                    ps = bone_scales.get(parent, [1.0, 1.0, 1.0]) if parent != 'root' else [1.0, 1.0, 1.0]
                    
                    # Scaled local offset
                    local_t = local_m[0:3, 3].copy()
                    local_t[0] *= ps[0]
                    local_t[1] *= ps[1]
                    local_t[2] *= ps[2]
                    
                    # Construct world matrix
                    m = p_mat.copy()
                    # World Position: Parent_Pos + Parent_Rot * Scaled_Offset
                    # We use p_mat basis (which is just rotation, no scale)
                    m[0:3, 3] = p_mat[0:3, 3] + p_mat[0:3, 0:3] @ local_t
                    # World Rotation: Parent_Rot * Local_Rot
                    m[0:3, 0:3] = p_mat[0:3, 0:3] @ local_m[0:3, 0:3]
                    
                    # Final bone matrix includes its OWN scale for voxel decomposition
                    # But we don't pass this scale down to children's basis
                    matrices[bone] = m @ scale_m
                else:
                    # Fallback
                    bx, by, bz = self.pose.get(bone, (0, 0, 0))
                    m = np.identity(4)
                    m[0:3, 3] = [bx, by, bz]
                    matrices[bone] = m @ scale_m
            else:
                bx, by, bz = self.pose.get(bone, (0, 0, 0))
                m = np.identity(4)
                m[0:3, 3] = [bx, by, bz]
                matrices[bone] = m @ scale_m
                
        return matrices

    def decompose_parts(self):
        """
        Splits the voxel cloud into separate lists per bone.
        Converts positions to be relative to the bone's rest pose (Local Space).
        Uses Inverse World Matrix to ensure correct orientation.
        """
        parts = {}
        
        # Pre-calculate inverse matrices for speed
        inv_matrices = {name: np.linalg.inv(m) for name, m in self.world_matrices.items()}
        
        for (vx, vy, vz), color in self.voxels.items():
            primary_bone = self.owners.get((vx, vy, vz), "root")
            
            # Ensure part bucket exists
            if primary_bone not in parts:
                parts[primary_bone] = {"voxels": []}
            
            if primary_bone in inv_matrices:
                # Transform World -> Local: V_local = Inverse(World_M) @ V_world
                v_world = np.array([vx, vy, vz, 1.0])
                v_local = inv_matrices[primary_bone] @ v_world
                lx, ly, lz = v_local[0], v_local[1], v_local[2]
            else:
                # Fallback to simple subtraction if no matrix available
                bx, by, bz = self.pose.get(primary_bone, (0, 0, 0))
                lx = vx - bx
                ly = vy - by
                lz = vz - bz
            
            parts[primary_bone]["voxels"].append([lx, ly, lz, color])
            
        return parts

    def export(self, output_path):
        skeleton_info = {
            "name": self.generator.blueprint['skeleton'],
            "topology": self.topology,
            "rest_pose": self.pose,
            "bone_scales": self.generator.bone_scales
        }
        
        # Check if skeleton class has bind matrices
        if hasattr(self.generator.skeleton_class, "BIND_MATRICES"):
            skeleton_info["bind_matrices"] = self.generator.skeleton_class.BIND_MATRICES

        data = {
            "unit_name": self.generator.blueprint['name'],
            "height": self.generator.height,
            "skeleton": skeleton_info,
            "parts": self.decompose_parts()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Calculate total voxels for logging
        total_voxels = sum(len(p['voxels']) for p in data['parts'].values())
        print(f"Exported decomposed model with {total_voxels} voxels across {len(data['parts'])} parts to {output_path}")

if __name__ == "__main__":
    # Integration test with generator
    from generator import VoxelGenerator
    
    gen = VoxelGenerator("blueprints/hero_mixamo.json")
    gen.generate_base_body()
    gen.symbolic_paint("textures/character_spritesheet.png")
    
    rigger = VoxelRigger(gen)
    output_dir = "sprite_to_3d/actor_assets/hero"
    os.makedirs(output_dir, exist_ok=True)
    rigger.export(os.path.join(output_dir, "rig.json"))
