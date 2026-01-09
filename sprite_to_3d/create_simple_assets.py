import json
import os
import sys
import struct
import tempfile
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vox_to_gltf import VoxToGltf, generate_palette_png
import scene_composer

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def create_simple_assets(rig_json_path, output_dir, prefix="base"):
    with open(rig_json_path, 'r') as f:
        rig_data = json.load(f)
    
    topology = rig_data['skeleton']['topology']
    rest_pose = rig_data['skeleton']['rest_pose']
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate common palette
    palette_path = os.path.join(output_dir, "palette_texture.png")
    generate_palette_png(palette_path)
    
    # Build a quick lookup for children to calculate lengths
    children_map = {}
    for child, parent in topology.items():
        if parent:
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(child)
            
    # Standard mapping for filenames
    mapping = {
        "mixamorig_Hips": "pelvis",
        "mixamorig_Spine": "spine",
        "mixamorig_Spine1": "spine1",
        "mixamorig_Spine2": "spine2",
        "mixamorig_Neck": "neck",
        "mixamorig_Head": "head",
        "mixamorig_LeftShoulder": "leftshoulder",
        "mixamorig_RightShoulder": "rightshoulder",
        "mixamorig_LeftArm": "arm_l",
        "mixamorig_RightArm": "arm_r",
        "mixamorig_LeftForeArm": "elbow_l",
        "mixamorig_RightForeArm": "elbow_r",
        "mixamorig_LeftHand": "hand_l",
        "mixamorig_RightHand": "hand_r",
        "mixamorig_LeftUpLeg": "thigh_l",
        "mixamorig_RightUpLeg": "thigh_r",
        "mixamorig_LeftLeg": "knee_l",
        "mixamorig_RightLeg": "knee_r",
        "mixamorig_LeftFoot": "foot_l",
        "mixamorig_RightFoot": "foot_r",
    }
    
    # Process each bone we care about (in the mapping)
    for bone_name, short_name in mapping.items():
        if bone_name not in rest_pose:
            print(f"Skipping {bone_name}, not in rest pose.")
            continue
            
        # Calculate Length
        length = 10.0 # Default length
        
        # Heuristic for length: distance to first child
        children = children_map.get(bone_name, [])
        if children:
            # Prefer specific children for branching bones
            target_child = children[0]
            if bone_name == "mixamorig_Hips":
                 # Hips connects to Spines and Legs. Usually we want the 'body' direction, maybe Spine?
                 if "mixamorig_Spine" in children: target_child = "mixamorig_Spine"
            
            p1 = rest_pose[bone_name]
            p2 = rest_pose[target_child]
            length = distance(p1, p2)
            
            # If length is tiny (e.g. toe base), default to something visible
            if length < 2.0: length = 5.0
        else:
            # Leaf bones
            if "Head" in bone_name: length = 8.0
            elif "Hand" in bone_name: length = 6.0
            elif "Foot" in bone_name: length = 8.0
        
        print(f"Generating {short_name} ({bone_name}) - Length: {length:.2f}")
        
        # Generate Voxels
        # X axis = Length. (0 to length)
        # Y/Z axis = Thickness (-1 to 1 => width 3)
        # Note: VoxWriter expects integer coordinates.
        
        voxels = []
        l_int = max(1, int(length))
        
        # Color: 153 (Reddish from palette? Or check palette.py. Using 153 as generic body color)
        color = 153 
        
        for x in range(l_int):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    # MagicaVoxel Space: X=Length, Y=Depth, Z=Height
                    # Our logic: X along bone.
                    voxels.append((x, y, z, color))
                    
        # Add a "joint" marker at 0,0,0 (Different color)
        voxels.append((0, 0, 0, 216)) # White/Bright
                    
        # Write temporary VOX
        writer = scene_composer.VoxWriter()
        model_idx = writer.add_model(voxels)
        # Place at 0,0,0
        instances = [(model_idx, (0, 0, 0), 0, "part")]
        
        with tempfile.NamedTemporaryFile(suffix=".vox", delete=False) as tmp:
            tmp_vox_path = tmp.name
            
        try:
            # Save VOX
            writer.save(tmp_vox_path, instances, no_center=True)
            
            # Export GLTF
            gltf_filename = f"{prefix}_{short_name}.gltf"
            gltf_path = os.path.join(output_dir, gltf_filename)
            
            converter = VoxToGltf(tmp_vox_path, no_center=True)
            converter.export(gltf_path)
            
            # Copy to preview assets if needed
            preview_hero_dir = os.path.join(os.path.dirname(__file__), "preview_v2", "assets", "hero")
            if os.path.exists(preview_hero_dir):
                import shutil
                shutil.copy(gltf_path, os.path.join(preview_hero_dir, gltf_filename))
                bin_filename = gltf_filename.replace(".gltf", ".bin")
                shutil.copy(gltf_path.replace(".gltf", ".bin"), os.path.join(preview_hero_dir, bin_filename))
                
        finally:
            if os.path.exists(tmp_vox_path):
                os.remove(tmp_vox_path)

if __name__ == "__main__":
    rig_path = "sprite_to_3d/vox_construction/hero_rig.json"
    out_dir = "sprite_to_3d/actor_assets/hero"
    
    if not os.path.exists(rig_path):
        print(f"Error: {rig_path} not found.")
        sys.exit(1)
        
    create_simple_assets(rig_path, out_dir)
