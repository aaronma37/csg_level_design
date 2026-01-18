# CSG Level Design (FFT-Style Paradigm)

This repository manages procedural voxel assets and tile-based level designs for a tactical RPG. It employs a neuro-symbolic approach, combining procedural generation (Python) with modular assembly (Lua).

## The 64x64 Tile Paradigm
The project has shifted to a **Final Fantasy Tactics** style layout system:
*   **Base Unit**: A **64x64 voxel tile**.
*   **Modular Tiles**: Each tile is a standalone Lua file in `csg_assets/tiles/`, containing layout and metadata (height, navigation, connections).
*   **Grid Assembly**: Scenes are assembled by placing these tiles on a grid in a scene layout file (`csg_assets/scenes/`).

## Project Structure
*   `/csg`: JSON definitions of base CSG assets.
*   `/csg_assets/tiles`: Modular 64x64 tiles.
*   `/csg_assets/scenes`: Grid-based level compositions.
*   `/generators`: Python scripts for procedural asset and tile generation.
*   `/patterns`: Shared procedural volumes and patterns (planks, bricks, etc.).
*   `/tools`: Utilities for compilation, conversion, and validation.

## Core Workflows
1.  **Generate Asset**: Create base geometry using Python generators.
2.  **Compile & Convert**: JSON -> VOX -> GLTF.
3.  **Define Tile**: Create a 64x64 tile Lua file combining assets with metadata.
4.  **Compose Scene**: Assemble tiles on a grid in a scene Lua file.
5.  **Deploy**: Sync tiles, scenes, and GLTF assets to the renderer (`love_exp`).

See [WORKFLOWS.md](./WORKFLOWS.md) for detailed execution steps.