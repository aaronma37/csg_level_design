# TODO: Custom Skeleton Limb Scaling

This document outlines the steps required to support custom scaling for individual limbs (bones) in the 3D character pipeline. Currently, bone thickness and lengths are largely hardcoded or based on fixed heuristics.

## 1. Blueprint System (`blueprints/*.json`)
- [ ] **Add `bone_scales` to Blueprint**: Update `UnitBlueprint` in `create_blueprint.py` to accept a dictionary of bone-specific scale factors.
  ```json
  "bone_scales": {
    "mixamorig_Head": [1.5, 1.5, 1.5],
    "mixamorig_RightArm": [1.0, 1.2, 1.0],
    "mixamorig_Hips": [1.2, 1.0, 1.2]
  }
  ```
- [ ] **Update Topology Definition**: Ensure that when a bone is scaled, its children are correctly offset in the T-pose calculation.

## 2. Skeleton Definition (`sprite_to_3d/skeletons/mixamo.py`)
- [ ] **Dynamic T-Pose Calculation**: Modify `get_t_pose(height)` to accept an optional `bone_scales` map.
- [ ] **Propagate Scale to Offsets**: When a bone length (e.g., Spine) is scaled, the cumulative Y-position of all bones above it (Spine1, Spine2, Neck, Head) must be adjusted accordingly.
- [ ] **Update Bind Matrices**: Ensure `BIND_MATRICES` generation accounts for the local scale of the bone.

## 3. Voxel Generation (`sprite_to_3d/generator.py`)
- [ ] **Integrate Scale into `radius_map`**: Instead of a global hardcoded `radius_map`, look up the `bone_scales` from the blueprint.
- [ ] **Adjust Capsule Radii**: Multiply the `r1, r2` values in `draw_tapered_capsule` by the X/Z scale of the bone.
- [ ] **Adjust Segment Length**: Use the bone's Y-scale to determine the distance between `p1` and `p2` if the T-pose doesn't already account for it.
- [ ] **Special Volume Scaling**: Scale the "Head Volume", "Hand Volume", and "Foot Volume" logic by the corresponding bone scales.

## 4. Rigger & Decomposition (`sprite_to_3d/rigger.py`)
- [ ] **Weighting Adjustments**: Ensure the voxel-to-bone ownership logic still functions correctly if bones are significantly larger/smaller (potential for overlapping volumes).
- [ ] **Local Space Normalization**: When decomposing voxels into local bone space, ensure the scale is handled such that the local voxels remain "normalized" or consistently sized relative to the bone's bind scale.

## 5. Modular Asset Creation (`sprite_to_3d/create_modular_assets.py`)
- [ ] **GLTF Export Scale**: Ensure `VoxToGltf` doesn't "bake" the scale in a way that makes it impossible for the engine to override. Ideally, assets are generated at "1.0 scale" relative to their bone, and the engine applies the final transform.

## 6. Engine / Previewer (`sprite_to_3d/preview_v2/actor.lua`)
- [ ] **Handle Non-Uniform Scale**: Verify `Actor:_build_skeleton` and `Actor:update` correctly decompose and apply the `temp_scale` from the `mat4`.
- [ ] **Bone Syncing**: Ensure `model:set_scale(bone:get_world_scale())` correctly transfers the limb's thickness/length from the animated bone to the flat modular mesh.
- [ ] **Animation Blending**: Check if scaling affects Mixamo animation playback (it shouldn't if using local rotations, but translations might need scaling).

## Implementation Order (Recommended)
1. **Blueprints**: Define the data structure.
2. **Skeleton**: Implement the math for offset propagation.
3. **Generator**: Make voxel thickness reactive to the new data.
4. **Actor**: Ensure the 3D engine displays the resulting non-uniform scales correctly.
