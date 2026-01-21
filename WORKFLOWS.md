# Workflows

## Core Principles
*   **Grid Integrity**: All tiles MUST conform to the **32x32** footprint (Standard).
*   **Palette Integrity**: `palette.py` is the master definition for materials. **Do not modify `palette.py` for temporary tasks**.

## Pipelines

### 1. CSG to Game Asset Pipeline
Creating procedural base geometry.

1.  **Generate Base Asset**: Run generator (from `generators/tiles/` or `generators/props/`).
    *   *Requirement*: The generator must import `primitives/floor_base_32.json` (or equivalent) to form the base.
    *   *Tagging*: Ensure the JSON output includes `"asset_tags": ["base"]` (or `"mega_base"`).
    ```bash
    python3 generators/tiles/generate_wall_stone_32.py
    ```
2.  **Compile to VOX**:
    ```bash
    python3 csg_compiler.py csg/wall_stone_32.json
    ```
3.  **Export to GLTF**: (Use `--no-center` for tiles to maintain grid alignment).
    ```bash
    python3 vox_to_gltf.py --no-center vox/floor_bevel_32_var1.vox csg/floor_bevel_32.gltf
    ```
4.  **Deploy**:
    ```bash
    cp csg/floor_bevel_32.gltf csg/floor_bevel_32.bin ~/love_exp/assets/csg_assets/
    ```

### 3. Iterating on an Asset (The Baking Loop)
How to create a new "Base Tile" (e.g., a Stone Wall on Grass).

1.  **Substrate (`generators/floors/`)**:
    *   Ensure the floor type exists (e.g., `floor_grass.py`).
    *   These scripts must expose a `get_instructions()` function for other generators to import.
2.  **Structure (`generators/tiles/`)**:
    *   Create the feature generator (e.g., `generate_wall_stone.py`).
    *   **Baking**: Import the substrate and "mash" it into your instructions.
    ```python
    from generators.floors import floor_grass
    instructions.extend(floor_grass.get_instructions(32, 32))
    # ... add wall instructions ...
    ```
    *   **Crucial**: Tag the result as `["base"]`.
3.  **Registry Update**:
    *   Add the new baked asset to `csg/asset_registry.json`.
4.  **Compile & Export**:
    *   `python3 csg_compiler.py csg/my_baked_asset.json`
    *   `./deploy_assets.sh` (converts to GLTF and updates Tile Registry).
5.  **Verify**:
    *   Check the result in `tactical_test_32.lua` or the ASCII visualizer.

### 4. Iterating on Procedural Generation
How to change the rules of the world or add new biome features.

1.  **Define the Rule**:
    *   Example: "Add a river that flows from North to West."
    *   Example: "Ensure no fireplaces are placed next to doors."

2.  **Tagging (The Prerequisite)**:
    *   The generator works on **Tags**, not filenames.
    *   Ensure your assets have the right tags in `csg/asset_registry.json` (e.g., `["river", "straight"]`).
    *   Ensure your tiles have the right tags in `csg_assets/tile_registry.json`.
    *   *Note*: `tile_registry.json` is auto-built by `tools/tile_registry.py` (run `deploy_assets.sh`).

3. **Theme Definition (`tools/procedural_gen.py`)**:
    *   **Define the Theme**: Add a new entry to the `THEMES` dictionary mapping logical roles (e.g., `wall_north`, `floor`) to specific asset tags.
    *   *Code Pattern*: `THEMES["my_biome"] = { "floor_primary": {"include": ["lava"]} }`

4. **Algorithm Update (Logic)**:
    *   **Phase 1 (Structure)**: Modify `generate_room` to change wall pools or exit logic.
    *   **Phase 2 (Pathing)**: Update `get_path` if you change walkability rules.
    *   **Phase 3 (Filling)**: Update the asset placement loops.
        *   *Code Pattern*: `query_registry(include=["my_new_tag"])`

5.  **Testing**:
    *   Run the generator directly with your theme:
    ```bash
    python3 tools/procedural_gen.py --name test_gen --width 12 --height 12 --theme tavern
    ```
5.  **Visualize**:
    *   **ASCII Check** (Fastest):
        ```bash
        lua visualize_scene.lua csg_assets/scenes/test_gen.lua
        cat csg_assets/scenes/test_gen.txt
        ```
    *   **Engine Check**:
        Deploy without recompiling (fast):
        ```bash
        ./deploy_assets.sh --no-recompile
        ```
        Open the game engine and load `test_gen`.

Assembling assets into a playable world.

1.  **Define Tile**: Create a Lua file in `csg_assets/tiles/`.
    *   Include `size = {32, 32}`.
    *   **Base Asset**: Must include exactly one asset tagged `base`.
    *   **Props**: Add decorations using `snap_to = 'base.socket_name'` (e.g., `base.mantle_left`).
2.  **Compile & Deploy**:
    *   Run the deployment script:
    ```bash
    ./deploy_assets.sh
    ```
    *   **The Compiler**: `deploy_assets.sh` automatically runs `tile_compiler.py`.
    *   **Resolution**: The compiler validates the "One Base Asset" rule and resolves all `snap_to` logic into explicit `pos` coordinates using Asset JSON metadata.
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
    