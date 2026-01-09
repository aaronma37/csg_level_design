# TODO: Custom Skeleton Limb Scaling

This document outlines the steps required to support custom scaling for individual limbs (bones) in the 3D character pipeline.

## 1. Blueprint System (`blueprints/*.json`)
- [x] **Add `bone_scales` to Blueprint**: Update `UnitBlueprint` in `create_blueprint.py` to accept a dictionary of bone-specific scale factors.
- [x] **Update Topology Definition**: Ensure that when a bone is scaled, its children are correctly offset in the T-pose calculation.

## 2. Skeleton Definition (`sprite_to_3d/skeletons/mixamo.py`)
- [x] **Dynamic T-Pose Calculation**: Modify `get_t_pose(height)` to accept an optional `bone_scales` map.
- [x] **Propagate Scale to Offsets**: When a bone length is scaled, the cumulative position of children is adjusted.
- [x] **Robust Matrix Parsing**: Handle various lengths of bind matrices (15, 16, 19 elements).

## 3. Voxel Generation (`sprite_to_3d/generator.py`)
- [x] **Integrate Scale into `radius_map`**: Look up `bone_scales` from the blueprint.
- [x] **Adjust Capsule Radii**: Multiply `r1, r2` by the X/Z scale of the bone.
- [x] **Adjust Segment Length**: Use bone's Y-scale for special volumes (Head, Hands, Feet).

## 4. Rigger & Decomposition (`sprite_to_3d/rigger.py`)
- [x] **Weighting Adjustments**: Inherit rotation but scale translation in world matrices.
- [x] **Local Space Normalization**: Voxel decomposition accounts for custom bone scales.

## 5. Modular Asset Creation (`sprite_to_3d/create_modular_assets.py`)
- [x] **GLTF Export Scale**: Assets are generated at 1.0 scale relative to their bones.

## 6. Engine / Previewer (`sprite_to_3d/preview_v2/actor.lua`)
- [x] **Apply Bone Scales**: `Actor:_build_skeleton` applies `bone_scales` to bone nodes.
- [x] **Fix Matrix Crash**: Added `ensure_16` helper to handle inconsistent matrix data.
- [ ] **Scale Animation Translations**: In `Actor:update`, scale the local position of animated bones by their parent's custom scale to keep the rig connected.

## Implementation Order (Remaining)
1. **Animation Scaling**: Fix the "joint detachment" during playback in `actor.lua`.