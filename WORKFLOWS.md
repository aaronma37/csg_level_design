# Workflows

## Core Principles
*   **Palette Integrity**: `palette.py` is the master definition for materials in CSG assets. It maps specific indices to material types (Wood, Stone, etc.) used by the renderer. **Do not modify `palette.py` for temporary tasks**; create separate palette files if needed. Always use `palette.py` for CSG definitions to ensure consistent material mapping.

## Pipelines

### CSG to Game Asset Pipeline
This workflow describes the process of creating a procedural asset and deploying it to the game engine.

1.  **Generate CSG**: Run a generator script (e.g., `generate_figurine.py`) to produce a CSG JSON definition (e.g., `figurine.json`). Note: Most generator scripts use relative paths and should be executed from within the `generators/` directory.
    ```bash
    cd generators
    python3 generate_chair.py
    cd ..
    ```
2.  **Compile to VOX**: Use the compiler to convert the JSON definition into a `.vox` model.
    ```bash
    python3 csg_compiler.py figurine.json
    ```
3.  **Export to GLTF**: Convert the `.vox` model to a GLTF asset using the exporter.
    ```bash
    python3 vox_to_gltf.py figurine.vox
    ```
4.  **Deploy**: Move the generated artifacts to the game project's asset directory.
    ```bash
    mv figurine.gltf figurine.bin ~/love_exp/assets/csg_assets/
    ```

### Sprite to Animated 3D Model Pipeline
This workflow bridges 2D pixel art and 3D animation by generating rigged voxel assets from sprites.

1.  **Schema (Phase 1)**: Define a `blueprint.json` mapping the sprite to a Skeleton and defining Primitives (hair, cape).
2.  **Generation (Phase 2)**: Generate volumetric mass for each primitive and paint it by projecting the sprite's colors.
3.  **Rigging (Phase 4)**: Assign bone weights and physics properties (elasticity, mass) to every voxel.
4.  **Baking (Phase 5)**: Simulate skeletal animations with soft-body physics, snap voxels back to the grid per-frame, and export as a sequence of GLTF meshes.




### Logical Composition Pipeline (Micro-Props)
This workflow is used for assets smaller than 16x16, or complex props made of repeating modular parts.

1.  **Define Logical Primitives**: Create a function in a `patterns/` file that builds a specific component (e.g., a `make_brick()` or `make_skull()`) using `VoxelBuilder`.
2.  **Compose Asset**: Create a generator script that imports these primitives and uses `builder.add_component(component, offset)` to arrange them.
3.  **Compile & Deploy**: Use the standard `csg_compiler.py` and `deploy_assets.sh` as usual.

### Layout Validation and Scene Generation
This workflow covers procedural layout creation, verification, and Lua scene export.

1.  **Generate Layout**: Run a layout generator to produce a scene JSON.
    ```bash
    python3 generators/generate_tavern_layout.py
    ```
2.  **Lint and Validate (MANDATORY)**: Run the linter to ensure characters are grounded and not stuck in walls.
    ```bash
    python3 tools/lint_layout.py csg/tavern_layout.json
    ```
    *Note: Use `tools/apply_tags.py` first if new assets were added.*
3.  **Compose Scene**: Convert the validated JSON into a Lua scene file for the game engine.
    ```bash
    python3 scene_composer.py csg/tavern_layout.json
    ```

## Notes
*   The `view_vox.sh` script does not work currently. Do not use it.
