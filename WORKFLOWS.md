# Workflows

## Core Principles
*   **Grid Integrity**: All tiles MUST conform to the **32x32** footprint (Standard).
*   **Palette Integrity**: `palette.py` is the master definition for materials. **Do not modify `palette.py` for temporary tasks**.

## Pipelines

### 1. CSG to Game Asset Pipeline
Creating procedural base geometry.

1.  **Generate CSG**: Run generator (from `generators/`).
    ```bash
    python3 generators/generate_floor_bevel_variants.py
    ```
2.  **Compile to VOX**:
    ```bash
    python3 csg_compiler.py csg/floor_bevel_32_var1.json
    ```
3.  **Export to GLTF**: (Use `--no-center` for tiles to maintain grid alignment).
    ```bash
    python3 vox_to_gltf.py --no-center vox/floor_bevel_32_var1.vox csg/floor_bevel_32.gltf
    ```
4.  **Deploy**:
    ```bash
    cp csg/floor_bevel_32.gltf csg/floor_bevel_32.bin ~/love_exp/assets/csg_assets/
    ```

### 2. Tile & Scene Composition Pipeline
Assembling assets into a playable world.

1.  **Define Tile**: Create a Lua file in `csg_assets/tiles/`.
    *   Include `size = {32, 32}`.
    *   Add metadata for `base_height`, `height_type`, and `nav_mask`.
    *   **Anchors & Snapping**: Use `snap_to = 'target_id.point'` and `snap_from = 'point'` to align assets semantically. (e.g., align wall `front` to floor `north`).
2.  **Compile & Deploy**:
    *   Run the deployment script:
    ```bash
    ./deploy_assets.sh
    ```
    *   **The Compiler**: `deploy_assets.sh` automatically runs `tile_compiler.py`.
    *   **Resolution**: The compiler reads your source Lua files in `csg_assets/tiles/`, resolves all `snap_to` logic into explicit `pos` coordinates using Asset JSON metadata, and writes the "Compiled" Lua to the game directory.
    *   **Direct Engine Input**: The Game Engine (`~/love_exp`) only sees the compiled files with explicit positions.
3.  **Compose Scene**: Create/Update a Lua file in `csg_assets/scenes/`.
    *   Define a `tiles` list using grid coordinates `{x, z}` (and optional `y` for height).
3.  **Deploy Logic**:
    *   Ensure all scene files are in `csg_assets/scenes/`.
    *   Run the deploy script or copy manually:
    ```bash
    ./deploy_assets.sh --no-recompile
    # OR
    cp csg_assets/scenes/*.lua ~/love_exp/assets/csg_assets/scenes/
    ```
    *   *Note*: `deploy_assets.sh` automatically updates the ASCII visualization (`.txt`) for `tactical_test_32.lua`.
    