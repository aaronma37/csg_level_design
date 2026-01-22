# CSG Asset Forge

This repository is a dedicated **Asset Forge** for a tactical RPG voxel engine. It uses a neuro-symbolic approach to procedurally generate high-quality 3D tiles from CSG (Constructive Solid Geometry) definitions.

## The Paradigm Shift
*   **This Repo (The Forge)**: Responsible for creating building blocks (Tiles). It compiles procedural logic into game-ready GLTF models and Lua metadata.
*   **Game Engine (The Architect)**: Responsible for level assembly. It dynamically loads layouts from ASCII files or generates rooms procedurally using the tiles published by this repo.

## Core Principles
*   **32x32 Grid**: Every tile conforms to a standard 32x32 voxel footprint.
*   **Atomic Tiles**: A tile is a standalone Lua file in `csg_assets/tiles/` containing metadata (tags, block size, lights) and geometry.
*   **Master Palette**: `palette.py` defines the material system.

## Key Workflows
1.  **Select Substrate**: Choose a floor pattern from `generators/floors/`.
2.  **Forge Asset**: Create a generator in `generators/tiles/` to bake structures onto the substrate.
3.  **Define Tile**: Create a Tile Lua file adding metadata and props to the base asset.
4.  **Publish**: Run `./deploy_assets.sh` to sync assets to the game engine.

## The Publisher (`deploy_assets.sh`)
The master build script. It performs hashing to skip unchanged assets, compiles modified JSONs to GLTF, refreshes registries, and publishes everything to the LÖVE engine directory.

## Tools
*   **`csg_compiler.py`**: Converts JSON CSG definitions into `.vox` models.
*   **`vox_to_gltf.py`**: Converts voxels to optimized GLTF models.
*   **`tile_compiler.py`**: Resolves logical anchors and injects lighting data into Tile Lua files.
