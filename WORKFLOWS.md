# Workflows

## 1. The Asset Forge Pipeline (Standard)
How to create a new game-ready building block.

1.  **Generate Base Geometry**: Run a generator (e.g., `python3 generators/tiles/generate_wall_stone_32.py`).
2.  **Define Tile Metadata**: Create a Lua file in `csg_assets/tiles/`.
    *   Set `block_size = {w, h}` (e.g., `{1, 1}` for standard, `{6, 1}` for mega-walls).
    *   Set `tile_tags = {"stone", "wall"}` for engine-side procgen search.
3.  **Publish**: Run `./deploy_assets.sh`.
    *   Modified JSONs are forged into GLTF models.
    *   Tile metadata is compiled and anchors are resolved.
    *   Assets are synced to `~/love_exp/assets/csg_assets/`.

## 2. Creating Mega-Tiles
For assets larger than 256 voxels (the VOX engine limit):
1.  **Split the Forge**: Create two separate generators (Part 1 and Part 2).
2.  **Continuity**: Use a `global_x_offset` in your noise functions to ensure patterns are seamless across the seam.
3.  **Tile Definition**: Create two separate Tile Lua files.
4.  **Assembly**: Place them side-by-side in your ASCII grid.

## 3. Maintenance & Validation
*   **Asset Audit**: `python3 tools/audit_tiles.py` ensures your base assets provide full floor coverage.
*   **Registry Check**: The publisher automatically updates `tile_registry.json`, which the engine uses for procedural generation.

## 4. Deprecated Workflows
*   **Python Procgen**: `tools/procedural_gen.py` is moved to `deprecated/`. Level generation now lives inside the engine logic.
*   **Static Scene Compilation**: `tools/ascii_to_scene.py` is moved to `deprecated/`. The engine now loads `.txt` files directly using `ascii_loader.lua`.
