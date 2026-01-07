import xml.etree.ElementTree as ET
import numpy as np
import os

def parse_matrix(matrix_str):
    return np.array([float(x) for x in matrix_str.split()]).reshape(4, 4)

def get_world_transform(node, ns, parent_transform=np.identity(4)):
    matrix_elem = node.find('ns:matrix', ns)
    local_transform = parse_matrix(matrix_elem.text)
    world_transform = parent_transform @ local_transform
    
    transforms = {node.get('id'): world_transform}
    for child in node.findall('ns:node', ns):
        transforms.update(get_world_transform(child, ns, world_transform))
    return transforms

def get_topology(node, ns):
    topology = {}
    node_id = node.get('id')
    for child in node.findall('ns:node', ns):
        topology[child.get('id')] = node_id
        topology.update(get_topology(child, ns))
    return topology

def extract(dae_path):
    tree = ET.parse(dae_path)
    root = tree.getroot()
    ns = {'ns': 'http://www.collada.org/2005/11/COLLADASchema'}
    
    visual_scene = root.find('.//ns:library_visual_scenes/ns:visual_scene', ns)
    hips_node = visual_scene.find(".//*[@id='mixamorig_Hips']", ns)
    
    topology = {"mixamorig_Hips": "root"}
    topology.update(get_topology(hips_node, ns))
    
    world_transforms = get_world_transform(hips_node, ns)
    
    # Extract LOCAL transforms too
    local_transforms = {}
    def get_local_transforms(node):
        matrix_elem = node.find('ns:matrix', ns)
        local_m = parse_matrix(matrix_elem.text)
        local_transforms[node.get('id')] = local_m
        for child in node.findall('ns:node', ns):
            get_local_transforms(child)
    get_local_transforms(hips_node)

    # Calculate height scale
    head_top = world_transforms.get('mixamorig_HeadTop_End')
    if head_top is not None:
        total_height = head_top[1, 3]
    else:
        total_height = world_transforms['mixamorig_Head'][1, 3]
    
    scale = 50.0 / total_height
    
    rest_pose = {}
    for bone, transform in world_transforms.items():
        pos = transform[:3, 3]
        rest_pose[bone] = (pos[0] * scale, pos[1] * scale, pos[2] * scale)

    # Scaled Local Matrices
    scaled_local_matrices = {}
    for bone, m in local_transforms.items():
        ms = m.copy()
        # Scale translation
        ms[0, 3] *= scale
        ms[1, 3] *= scale
        ms[2, 3] *= scale
        scaled_local_matrices[bone] = ms.flatten().tolist()

    # Generate Python class
    output = []
    output.append("class MixamoSkeleton:")
    output.append("    TOPOLOGY = {")
    output.append("        'root': None,")
    for child, parent in topology.items():
        output.append(f"        '{child}': '{parent}',")
    output.append("    }")
    output.append("")
    output.append("    BIND_MATRICES = {")
    for bone, m_list in scaled_local_matrices.items():
        m_str = ", ".join(f"{x:.6f}" for x in m_list)
        output.append(f"        '{bone}': [{m_str}],")
    output.append("    }")
    output.append("")
    output.append("    @classmethod")
    output.append("    def get_topology(cls):")
    output.append("        return cls.TOPOLOGY")
    output.append("")
    output.append("    @classmethod")
    output.append("    def get_bones(cls):")
    output.append("        return list(cls.TOPOLOGY.keys())")
    output.append("")
    output.append("    @classmethod")
    output.append("    def get_t_pose(cls, height):")
    output.append("        scale = height / 50.0")
    output.append("        ref_pose = {")
    output.append("            'root': (0, 0, 0),")
    for bone, (x, y, z) in rest_pose.items():
        output.append(f"            '{bone}': ({x:.4f}, {y:.4f}, {z:.4f}),")
    output.append("        }")
    output.append("        scaled_pose = {}")
    output.append("        for bone, (x, y, z) in ref_pose.items():")
    output.append("            scaled_pose[bone] = (x * scale, y * scale, z * scale)")
    output.append("        return scaled_pose")

    with open("sprite_to_3d/skeletons/mixamo.py", "w") as f:
        f.write("\n".join(output))
    print("Generated sprite_to_3d/skeletons/mixamo.py")

if __name__ == "__main__":
    extract("sprite_to_3d/imports/Standard Walk.dae")
