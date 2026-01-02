# Workflows

## Core Principles
*   **Palette Integrity**: `palette.py` is the master definition for materials in CSG assets. It maps specific indices to material types (Wood, Stone, etc.) used by the renderer. **Do not modify `palette.py` for temporary tasks** (like space carving); create separate palette files if needed. Always use `palette.py` for CSG definitions to ensure consistent material mapping.

## Pipelines

### CSG to Game Asset Pipeline
This workflow describes the process of creating a procedural asset and deploying it to the game engine.

1.  **Generate CSG**: Run a generator script (e.g., `generate_figurine.py`) to produce a CSG JSON definition (e.g., `figurine.json`).
2.  **Compile to VOX**: Use the compiler to convert the JSON definition into a `.vox` model.
    ```bash
    python csg_compiler.py figurine.json
    ```
3.  **Export to GLTF**: Convert the `.vox` model to a GLTF asset using the exporter.
    ```bash
    python vox_to_gltf.py figurine.vox
    ```
4.  **Deploy**: Move the generated artifacts to the game project's asset directory.
    ```bash
    mv figurine.gltf figurine.bin ~/love_exp/assets/csg_assets/
    ```

### Asset Iteration
*   **Creating an asset**: Create a python generation script given a description. After iterating on the asset parameters, ensure it is added to the scene layout (e.g., `tavern_layout.json`) and compile the full scene if necessary.

## Notes
*   The `view_vox.sh` script does not work currently. Do not use it.