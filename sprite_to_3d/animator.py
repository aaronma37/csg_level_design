import json
import math
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skeletons.humanoid import HumanoidSkeleton
from animations import WalkAnimation
from tools.builder import VoxelBuilder

def get_rotation_matrix(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    
    # ZYX order
    Rx = np.array([[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]])
    Ry = np.array([[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]])
    Rz = np.array([[cz, -sz, 0, 0], [sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    
    return Rz @ Ry @ Rx

def get_translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

class VoxelAnimator:
    def __init__(self, rigged_json_path):
        with open(rigged_json_path, 'r') as f:
            self.data = json.load(f)
        
        self.parts = self.data['parts'] # Now a dict: bone_name -> { voxels: [...] }
        self.height = self.data['height']
        self.topology = self.data['skeleton']['topology']
        self.rest_pose = self.data['skeleton']['rest_pose']
        
        # Ensure rest_pose values are tuples
        for k, v in self.rest_pose.items():
            self.rest_pose[k] = tuple(v)

    def animate_frame(self, animation, frame_idx):
        pose_data = animation.get_pose(frame_idx)
        is_matrix = getattr(animation, 'type', 'euler') == 'matrix'
        
        # 1. Calculate World Matrices for Current Pose
        world_matrices = {}
        bones = list(self.topology.keys())
        
        # Parent-first ordering
        ordered_bones = []
        visited = set()
        while len(ordered_bones) < len(bones):
            for b in bones:
                if b in visited: continue
                parent = self.topology[b]
                if parent is None or parent in visited:
                    ordered_bones.append(b)
                    visited.add(b)

        for bone in ordered_bones:
            parent = self.topology[bone]
            
            if is_matrix:
                m_data = pose_data.get(bone)
                if m_data:
                    local_m = np.array(m_data).reshape(4, 4)
                else:
                    # Identity if missing
                    local_m = np.identity(4)
                
                if parent is None:
                    world_matrices[bone] = local_m
                else:
                    world_matrices[bone] = world_matrices[parent] @ local_m
            else:
                # Euler path (legacy/fallback)
                rot = pose_data.get(bone, (0, 0, 0))
                rot_m = get_rotation_matrix(*rot)
                bx, by, bz = self.rest_pose[bone]
                
                if parent is None:
                    world_matrices[bone] = rot_m
                else:
                    px, py, pz = self.rest_pose[parent]
                    local_trans = get_translation_matrix(bx - px, by - py, bz - pz)
                    world_matrices[bone] = world_matrices[parent] @ local_trans @ rot_m

        # 2. Transform Parts
        new_grid = {} # (x,y,z) -> color_index
        
        for bone_name, part_data in self.parts.items():
            if bone_name not in world_matrices:
                continue
                
            mat = world_matrices[bone_name]
            
            for v_data in part_data['voxels']:
                lx, ly, lz, color = v_data
                local_pos = np.array([lx, ly, lz, 1.0])
                
                # Transform: World = Matrix * Local
                final_pos = mat @ local_pos
                
                # 3. Quantize (The Snap) - For Baking Preview ONLY
                # In a real engine, we'd render the mesh at float coordinates.
                qx, qy, qz = int(round(final_pos[0])), int(round(final_pos[1])), int(round(final_pos[2]))
                
                new_grid[(qx, qy, qz)] = color
            
        return new_grid

    def bake_animation(self, animation, output_dir, name_prefix):
        os.makedirs(output_dir, exist_ok=True)
        import scene_composer
        from linter import lint_model
        
        for f in range(animation.duration):
            print(f"Baking frame {f+1}/{animation.duration}...")
            grid = self.animate_frame(animation, f)
            
            # Convert to VOX for export
            writer = scene_composer.VoxWriter()
            
            packed_voxels = []
            for (x, y, z), c in grid.items():
                # Correct orientation for MagicaVoxel (X, Z, Y)
                packed_voxels.append((x, z, y, c))
                
            model_idx = writer.add_model(packed_voxels)
            instances = [(model_idx, (0, 0, 0), 0, f"frame_{f}")]
            
            vox_path = os.path.join(output_dir, f"{name_prefix}_{f:02d}.vox")
            writer.save(vox_path, instances)
            
            # Convert to GLTF (Using our tool)
            gltf_path = vox_path.replace(".vox", ".gltf")
            # We can't easily call the CLI here without overhead, but we can import it
            from vox_to_gltf import VoxToGltf, generate_palette_png
            generate_palette_png() # Ensure palette is in sync
            VoxToGltf(vox_path).export(gltf_path)

    def export_animation(self, animation, output_path):
        data = {
            "duration": animation.duration,
            "type": getattr(animation, 'type', 'euler'),
            "frames": []
        }
        
        for f in range(animation.duration):
            pose = animation.get_pose(f)
            # Convert tuples/numpy arrays to lists for JSON
            frame_data = {}
            for k, v in pose.items():
                if isinstance(v, (list, tuple)):
                    frame_data[k] = list(v)
                elif hasattr(v, 'tolist'):
                    frame_data[k] = v.tolist()
                else:
                    frame_data[k] = v
            data["frames"].append(frame_data)
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported animation data to {output_path}")

if __name__ == "__main__":
    from animations import JsonAnimation
    
    animator = VoxelAnimator("sprite_to_3d/actor_assets/hero/rig.json")
    # Load the matrix animation we extracted from DAE
    anim = JsonAnimation("sprite_to_3d/actor_assets/hero/walk.json")
    
    # Export Animation Data for Runtime Preview
    animator.export_animation(anim, "sprite_to_3d/actor_assets/hero/walk.json")
    
    # Bake for legacy/debug check (optional, but keeping it for now)
    # animator.bake_animation(anim, "output/walk_cycle", "hero_walk")
