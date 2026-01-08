import json
import os
import sys
import struct
import tempfile

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vox_to_gltf import VoxToGltf, generate_palette_png
import scene_composer

def create_modular_assets(rig_json_path, output_dir, prefix="base"):
    with open(rig_json_path, 'r') as f:
        rig_data = json.load(f)
    
    parts = rig_data['parts']
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate common palette
    palette_path = os.path.join(output_dir, "palette_texture.png")
    generate_palette_png(palette_path)
    
    for bone_name, data in parts.items():
        voxels = data['voxels']
        if not voxels:
            continue
            
        # Strip mixamorig_ prefix and convert to lowercase for filename
        clean_name = bone_name.replace("mixamorig_", "").lower()
        # Some specific mappings to match user preference if possible
        mapping = {
            "rightforearm": "elbow_r",
            "leftforearm": "elbow_l",
            "rightarm": "arm_r",
            "leftarm": "arm_l",
            "rightupleg": "thigh_r",
            "leftupleg": "thigh_l",
            "rightleg": "knee_r",
            "leftleg": "knee_l",
            "rightfoot": "foot_r",
            "leftfoot": "foot_l",
            "righthand": "hand_r",
            "lefthand": "hand_l",
            "head": "head",
            "hips": "pelvis"
        }
        filename_part = mapping.get(clean_name, clean_name)
        gltf_filename = f"{prefix}_{filename_part}.gltf"
        gltf_path = os.path.join(output_dir, gltf_filename)
        
        print(f"Exporting {bone_name} -> {gltf_path}")
        
        # Create a temporary .vox file for this part
        # VoxWriter expects (x, y, z, c) but recompose_world in VoxToGltf 
        # expects MagicaVoxel's (x, y, z) which it then transforms to (x, z, y).
        # Wait, VoxToGltf.mesh() does: gltf_pt = [float(pt[0]), float(pt[2]), float(pt[1])]
        # So it swaps Y and Z.
        
        # VoxelRigger.decompose_parts saved as [lx, ly, lz, color]
        # where Y is up.
        # VoxToGltf expects input voxels to be in MagicaVoxel space (Z up).
        # But wait, if we want to preserve (lx, ly, lz) where Y is up,
        # we should pass them as (lx, lz, ly) to VOX, 
        # so that VOX-Z (up) gets the Y-up value.
        
        # VoxelRigger.decompose_parts saved as [vx, vy, vz, color] 
        # where vy is character-height (Y-up).
        # To make it local to the bone, we subtract the bone rest position.
        bone_rest_pos = rig_data["skeleton"]["rest_pose"][bone_name]
        
        local_voxels = []
        for vx, vy, vz, color in voxels:
            # 1. Localize to bone pivot (Still in Y-up character space)
            lx = vx - bone_rest_pos[0]
            ly = vy - bone_rest_pos[1]
            lz = vz - bone_rest_pos[2]
            
            # 2. Convert to MagicaVoxel space (Z-up)
            # Character Y (height) -> VOX Z (height)
            # Character Z (forward) -> VOX Y (depth)
            # Character X (right) -> VOX X (width)
            local_voxels.append((int(lx), int(lz), int(ly), color))
            
        writer = scene_composer.VoxWriter()
        model_idx = writer.add_model(local_voxels)
        # Place at (0,0,0) in the temporary VOX world
        instances = [(model_idx, (0, 0, 0), 0, "part")]
        
        with tempfile.NamedTemporaryFile(suffix=".vox", delete=False) as tmp:
            tmp_vox_path = tmp.name
        
        try:
            writer.save(tmp_vox_path, instances)
            
            # Convert to GLTF
            converter = VoxToGltf(tmp_vox_path)
            converter.export(gltf_path)
        finally:
            if os.path.exists(tmp_vox_path):
                os.remove(tmp_vox_path)

if __name__ == "__main__":
    rig_path = "sprite_to_3d/vox_construction/hero_rig.json"
    out_dir = "sprite_to_3d/actor_assets/hero"
    
    if not os.path.exists(rig_path):
        print(f"Error: {rig_path} not found. Run generator.py and rigger.py first.")
        sys.exit(1)
        
    create_modular_assets(rig_path, out_dir)
