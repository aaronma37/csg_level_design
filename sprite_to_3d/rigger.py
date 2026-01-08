import json
import math
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class VoxelRigger:
    def __init__(self, generator):
        self.generator = generator
        self.voxels = generator.builder.voxels
        self.owners = generator.voxel_owners
        self.pose = generator.pose
        self.topology = generator.blueprint['topology']
        
    def decompose_parts(self):
        """
        Splits the voxel cloud into separate lists per bone.
        Converts positions to be relative to the bone's rest pose (Local Space).
        Returns:
            {
                "bone_name": {
                    "voxels": [[lx, ly, lz, color_idx], ...]
                },
                ...
            }
        """
        parts = {}
        
        for (vx, vy, vz), color in self.voxels.items():
            primary_bone = self.owners.get((vx, vy, vz), "root")
            
            # Ensure part bucket exists
            if primary_bone not in parts:
                parts[primary_bone] = {"voxels": []}
            
            # Get Bone Rest Position (Pivot)
            # Default to (0,0,0) if bone not found in pose (fallback)
            bx, by, bz = self.pose.get(primary_bone, (0, 0, 0))
            
            # Calculate Local Position
            lx = vx - bx
            ly = vy - by
            lz = vz - bz
            
            parts[primary_bone]["voxels"].append([lx, ly, lz, color])
            
        return parts

    def export(self, output_path):
        skeleton_info = {
            "name": self.generator.blueprint['skeleton'],
            "topology": self.topology,
            "rest_pose": self.pose
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
