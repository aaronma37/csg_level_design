import xml.etree.ElementTree as ET
import json
import numpy as np
import os
import sys

def extract_animation_matrices(dae_path, out_path, scale):
    tree = ET.parse(dae_path)
    root = tree.getroot()
    ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}

    animations = root.findall('.//ns:library_animations/ns:animation', ns)
    
    # We might have nested animations or flat list
    # If flat list, find all animations that target a joint matrix
    
    channels = root.findall('.//ns:library_animations//ns:channel', ns)
    
    bone_anims = {}
    max_frames = 0
    
    for channel in channels:
        target = channel.get('target')
        if not target or not target.endswith('/matrix'):
            continue
            
        bone_id = target.split('/')[0]
        sampler_id = channel.get('source')[1:]
        
        # Find sampler
        sampler = root.find(f".//ns:sampler[@id='{sampler_id}']", ns)
        output_src_id = sampler.find("./ns:input[@semantic='OUTPUT']", ns).get('source')[1:]
        
        # Find output source
        output_src = root.find(f".//ns:source[@id='{output_src_id}']", ns)
        float_array = output_src.find("ns:float_array", ns)
        data = [float(x) for x in float_array.text.split()]
        
        # Matrix is 16 floats
        matrices = [data[i:i+16] for i in range(0, len(data), 16)]
        
        scaled_matrices = []
        for m in matrices:
            # Scale translation (indices 3, 7, 11 for row-major 4x4)
            ms = list(m)
            
            # Mixamo Hips usually have translation in the animation
            # We want to keep the RELATIVE movement from the first frame or bind pose
            # But Standard Walk might be in-place or moving forward.
            # If it's moving forward, we might want to zero out the Z (forward in DAE)
            
            ms[3] *= scale
            ms[7] *= scale
            ms[11] *= scale
            
            # FOR IN-PLACE: Zero out the forward/sideways drift if it's the root
            if bone_id == "mixamorig_Hips":
                # Only keep vertical bobbing (Y in DAE is Y-up)
                # ms[3] = m_bind_pos_x * scale
                # ms[11] = m_bind_pos_z * scale
                pass
                
            scaled_matrices.append(ms)
            
        bone_anims[bone_id] = scaled_matrices
        max_frames = max(max_frames, len(scaled_matrices))

    # Reorganize into frames
    frames = []
    for f in range(max_frames):
        frame_data = {}
        for bone_id, matrices in bone_anims.items():
            if f < len(matrices):
                frame_data[bone_id] = matrices[f]
        frames.append(frame_data)
        
    with open(out_path, 'w') as f:
        json.dump({"duration": max_frames, "frames": frames, "type": "matrix"}, f, indent=2)
    
    print(f"Extracted matrix animation with {max_frames} frames to {out_path}")

if __name__ == "__main__":
    # We need to calculate the scale first. 
    # Usually we can get it from the skeleton we generated.
    # For now, I'll hardcode it or calculate it on the fly if I can.
    
    # Better: use the same logic as extract_mixamo_skeleton.py
    def get_scale(dae_path):
        tree = ET.parse(dae_path)
        root = tree.getroot()
        ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}
        
        # Simplified height calculation
        # Find HeadTop_End in visual scenes
        head_top_node = root.find(".//ns:node[@id='mixamorig_HeadTop_End']", ns)
        if head_top_node is None:
             head_top_node = root.find(".//ns:node[@id='mixamorig_Head']", ns)
             
        # This is non-trivial to get world Y without full traversal
        # But we know from previous run total_height was ~180-200
        # Let's just use 50.0 / total_height from extract_mixamo_skeleton
        return None # We'll let the user provide it or we'll look at the generated skeleton
        
    # Actually, let's just use 0.278 (approx 50/180) or similar
    # Wait, extract_mixamo_skeleton.py already ran and generated the skeleton.
    # I can just import it!
    sys.path.append(os.path.join(os.path.dirname(__file__), 'skeletons'))
    from skeletons.mixamo import MixamoSkeleton
    
    # Calculate scale based on rest pose HeadTop_End Y
    pose = MixamoSkeleton.get_t_pose(50)
    # The skeleton.py has coordinates already scaled to 50 height.
    # So we need to find the scale between the DAE and 50.
    
    # Let's just re-calculate total_height from DAE directly in this script
    def calculate_dae_height(dae_path):
        import xml.etree.ElementTree as ET
        import numpy as np
        tree = ET.parse(dae_path)
        root = tree.getroot()
        ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}
        
        def parse_matrix(matrix_str):
            return np.array([float(x) for x in matrix_str.split()]).reshape(4, 4)

        def get_world_y(node, parent_transform=np.identity(4)):
            matrix_elem = node.find('ns:matrix', ns)
            local_transform = parse_matrix(matrix_elem.text)
            world_transform = parent_transform @ local_transform
            y = world_transform[1, 3]
            
            max_y = y
            for child in node.findall('ns:node', ns):
                max_y = max(max_y, get_world_y(child, world_transform))
            return max_y

        visual_scene = root.find('.//ns:library_visual_scenes/ns:visual_scene', ns)
        hips_node = visual_scene.find(".//*[@id='mixamorig_Hips']", ns)
        return get_world_y(hips_node)

    dae_path = "sprite_to_3d/imports/Standard Walk.dae"
    dae_height = calculate_dae_height(dae_path)
    scale = 50.0 / dae_height
    print(f"DAE Height: {dae_height}, Scale: {scale}")
    
    extract_animation_matrices(dae_path, "sprite_to_3d/preview_v2/hero_anim.json", scale)
