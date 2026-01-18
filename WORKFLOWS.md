# Workflows

## Core Principles
*   **Grid Integrity**: All tiles MUST conform to the **64x64** footprint.
*   **Palette Integrity**: `palette.py` is the master definition for materials. **Do not modify `palette.py` for temporary tasks**.

## Pipelines

### 1. CSG to Game Asset Pipeline
Creating procedural base geometry.

1.  **Generate CSG**: Run generator (from `generators/`).
    ```bash
    python3 generators/generate_floor_64.py
    ```
2.  **Compile to VOX**:
    ```bash
    python3 csg_compiler.py csg/floor_64.json
    ```
3.  **Export to GLTF**: (Use `--no-center` for tiles to maintain grid alignment).
    ```bash
    python3 vox_to_gltf.py --no-center vox/floor_64.vox csg/floor_64.gltf
    ```
4.  **Deploy**:
    ```bash
    cp csg/floor_64.gltf csg/floor_64.bin ~/love_exp/assets/csg_assets/
    ```

### 2. Tile & Scene Composition Pipeline
Assembling assets into a playable world.

1.  **Define Tile**: Create a Lua file in `csg_assets/tiles/`.
    *   Include `size = {64, 64}`.
    *   Add metadata for `base_height`, `height_type`, and `nav_mask`.
2.  **Compose Scene**: Create/Update a Lua file in `csg_assets/scenes/`.
    *   Define a `tiles` list using grid coordinates `{x, y}`.
3.  **Deploy Logic**: Copy the Lua files to the renderer.
    ```bash
    cp csg_assets/scenes/*.lua ~/love_exp/assets/csg_assets/scenes/
        ```
    