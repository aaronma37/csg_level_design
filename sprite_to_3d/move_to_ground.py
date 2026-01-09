import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scene_composer

def move_to_ground(input_vox, output_vox):
    # Use load_vox_voxels from scene_composer
    voxels = scene_composer.load_vox_voxels(input_vox)
    
    if not voxels:
        print(f"Error: No voxels found in {input_vox}")
        return

    # voxels is a list of (x, y, z, c)
    # In .vox files, Z is UP (based on our export logic in generator.py)
    min_z = min(v[2] for v in voxels)
    
    print(f"Grounding model: Min Z is {min_z}. Shifting by {-min_z}")
    
    grounded_voxels = []
    for x, y, z, c in voxels:
        grounded_voxels.append((x, y, z - min_z, c))
        
    writer = scene_composer.VoxWriter()
    model_idx = writer.add_model(grounded_voxels)
    # We save with no_center=True to keep coordinates exactly as they are
    instances = [(model_idx, (0, 0, 0), 0, "grounded")]
    writer.save(output_vox, instances, no_center=True)
    print(f"Saved grounded model to {output_vox}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 move_to_ground.py <input.vox> <output.vox>")
    else:
        move_to_ground(sys.argv[1], sys.argv[2])
