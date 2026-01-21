# CSG Level Design (FFT-Style Paradigm)

This repository manages procedural voxel assets and tile-based level designs for a tactical RPG. It employs a neuro-symbolic approach, combining procedural generation (Python) with modular assembly (Lua).

## The 32x32 Tile Paradigm
The project has shifted to a **Final Fantasy Tactics** style layout system:
*   **Base Unit**: A **32x32 voxel tile**.
*   **Modular Tiles**: Each tile is a standalone Lua file in `csg_assets/tiles/`, containing layout and metadata (height, navigation, connections).
*   **Grid Assembly**: Scenes are assembled by placing these tiles on a grid in a scene layout file (`csg_assets/scenes/`).

## Project Structure
*   `/csg`: JSON definitions of base CSG assets.
*   `/csg_assets/tiles`: Modular 32x32 tiles.
*   `/csg_assets/scenes`: Grid-based level compositions.
*   `/generators/floors`: Substrate generators (Grass, Wood, Stone) used as bases.
*   `/generators/tiles`: Structure generators (Walls, Pillars) that bake features onto substrates.
*   `/generators/props`: Decoration generators (Furniture, Clutter).
*   `/patterns`: Shared procedural volumes and patterns (planks, bricks, etc.).
*   `/tools`: Utilities for compilation, conversion, and validation.

## Core Workflows
1.  **Select Substrate**: Choose a floor pattern from `generators/floors/`.
2.  **Bake Structure**: Create a Base Asset in `generators/tiles/` by mashing the substrate with a feature (Wall, Corner).
3.  **Compile & Convert**: JSON -> VOX -> GLTF.
4.  **Define Tile**: Create a 32x32 tile Lua file adding metadata and Props to the Base Asset.
5.  **Compose Scene**: Assemble tiles via `tools/procedural_gen.py` or manually.
6.  **Deploy**: Sync to the renderer.

See [WORKFLOWS.md](./WORKFLOWS.md) for detailed execution steps.

## Key Tools
*   **`tile_compiler.py`** (Root): The engine room. Compiles semantic Tile Lua files (with `snap_to` logic) into explicit, engine-ready Lua files. Enforces the "One Base Asset" rule.
*   **`tools/procedural_gen.py`**: The level generator. Generates complete scene Lua files (`csg_assets/scenes/`) by semantically assembling tiles based on constraints (e.g., "Create a 10x10 room with a North exit").
*   **`csg_compiler.py`** (Root): Converts JSON CSG definitions into `.vox` models.
*   **The Registry** (`csg/asset_registry.json` & `csg_assets/tile_registry.json`): The database of tags and metadata. Essential for the procedural generator to find assets by type (e.g., "get all walls").