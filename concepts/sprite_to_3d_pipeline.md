# Sprite to Animated 3D Model Pipeline

## Overview
This pipeline describes a high-fidelity workflow for creating rich, animated 3D voxel assets from 2D sprite references. The goal is to bridge the gap between retro/voxel aesthetics and modern skeletal animation by using Neurosymbolic AI to generate voxel structures, simulating soft-body physics, and "baking" the results into grid-snapped stop-motion animation sequences.

## Workflow Phases

### Phase 1: Schema Definition (Blueprints)
**Goal:** Define *what* the object is before generating geometry.
1.  **Skeleton Selection:**
    *   Analyze input sprite dimensions (pixels to voxels).
    *   Match against an existing Skeleton Library (e.g., `Humanoid_V2`).
    *   If no match exists, trigger creation of a new skeleton.
2.  **Unit Asset Definition:**
    *   Define components (hats, capes, weapons) as **Primitives** rather than raw voxels.
    *   **Metadata:**
        *   **Attachment Point:** Parent bone/joint (e.g., `CervicalSpine`).
        *   **Physics Type:** Behavior class (e.g., `Ribbon` for capes, `Rigid` for helmets).
3.  **Output:** A `blueprint.json` defining the unit's structure and primitive composition.

### Phase 2: Volumetric Generation & Painting
**Goal:** Create the static, T-posed 3D mass.
1.  **Mass Generation:**
    *   Instantiate volume for each component in the blueprint using Logical Placement, CSG, or SDF.
    *   Use specialized generators for dynamic shapes (e.g., spline extrusion for ribbons).
2.  **Surface Projection:**
    *   Project the 2D reference sprite onto the generated 3D volume.
    *   **Palette Mapping:** Match projected colors to `palette.py`. Dynamically append new colors if no close match exists, preserving palette integrity.
3.  **Output:** A segmented, painted voxel model in a reference pose.

### Phase 3: Validation & Iteration
**Goal:** Ensure technical and visual quality.
1.  **Automated Linting:**
    *   Check for floating voxels (disconnected islands).
    *   Verify structural integrity (no single-voxel weak points).
2.  **User Review:**
    *   Display the asset in the 3D `previewer`.
    *   User provides feedback (e.g., "Cape too thick," "Sword too low").
3.  **Refinement:** Adjust blueprint parameters or generation logic and regenerate until approved.

### Phase 4: Rigging & Data Preparation
**Goal:** Create a "Smart Voxel Cloud" aware of simulation properties.
1.  **Data Structuring:** Flatten the model into a list/database of voxels.
2.  **Voxel Attributes:**
    *   **Position:** `{x, y, z}` in rest pose.
    *   **Color:** Palette index.
    *   **Bone ID:** Primary parent bone.
    *   **Bone Weight:** Soft deformation influence.
    *   **Simulation Props:** Inertia, elasticity, mass (derived from Primitive type).
3.  **Semantic Enrichment:** Use the reference sprite to fine-tune weights (e.g., rigid chest vs. flowing hair).

### Phase 5: Animation & Baking
**Goal:** Generate the final stop-motion assets.
1.  **Animation Reuse:** Apply shared skeletal animations (Run, Attack) to the rig.
2.  **Simulation:**
    *   Run soft-body/physics simulation per frame.
    *   Calculate continuous positions for every voxel.
3.  **Quantization (The Snap):**
    *   Round continuous positions to the nearest integer grid coordinate.
    *   Resolve collisions (depth/priority) to maintain grid validity.
4.  **Export:**
    *   **Greedy Meshing:** Optimize the mesh for the current frame.
    *   **GLTF Sequence:** Export a unique mesh per frame (e.g., `run_01.gltf`, `run_02.gltf`).

### Phase 6: Custom Format Optimization (Stretch Goal)
**Goal:** optimize storage and runtime performance.
1.  **Format (.vxb):** "Voxel Binary" - a custom binary format.
2.  **Data:** Stores precision grid coordinates (0-255), face normals (6 directions), and palette indices.
3.  **Compression:** LZ4 compression on the binary blob.
4.  **Runtime:** Game engine decodes and streams geometry on the fly.
