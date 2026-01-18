# Layout Standards & Conventions (Tile Paradigm)

## 1. Coordinate System
*   **Vertical (Z-Up)**: 1 Unit = 1 Voxel.
*   **Horizontal (X, Y)**: 1 Unit = 1 Voxel.
*   **The Grid**: Standard Tiles are **64x64** voxels.
*   **Scene Grid**: Positions in scene files are expressed as grid indices `{x, y}` (e.g., `{0, 0}`, `{1, 0}`).

## 2. Tile Architecture
Every tile is a 64x64 "slice" of the map. 
*   **Self-Contained**: Tiles should generally include their own floor asset (`floor_64`) if they represent a walkable or solid area.
*   **Height Tiers**: Standard elevation increments are **16 units**.
    *   Tier 0: Z=0
    *   Tier 1: Z=16
    *   Tier 2: Z=32
*   **Metadata**:
    *   `base_height`: The elevation for character navigation.
    *   `height_type`: `flat` or `slope`.
    *   `nav_mask`: `1` for walkable, `0` for blocked.

## 3. Anchors & Pivots
*   **Tiles**: Anchored at their center relative to the grid cell.
*   **Assets within Tiles**: 
    *   Floor assets should be centered at `{0, 0}` within the tile.
    *   Furniture and Clutter are positioned relative to the tile's center.

## 4. Dollhouse Strategy (Visibility)
Since the camera is fixed at a South-West perspective:
*   **North/East Edges**: Use these for tall structures (walls, pillars, high shelves).
*   **South/West Edges**: Keep clear or use low-profile "cutaway" assets.
*   **Modular Walls**: Walls should be designed as 64-unit segments that can be swapped into a tile's `layout`.

## 5. Tile Hierarchy
*   **Level 0: Assets** (`floor_64.gltf`, `chair.gltf`) - The raw geometry.
*   **Level 1: Tiles** (`floor_wood_64.lua`, `dining_table_64.lua`) - Combinations of assets + navigation metadata.
*   **Level 2: Scenes** (`tavern_grid.lua`) - A collection of tiles arranged on the global grid.

## 6. Z-Stacking (Voxel-Clean Pass)
*   **Z=0**: Sub-floor/Backing.
*   **Z=1**: Surface planks/Tile top.
*   **Z=2**: Furniture base contact.
*   **Z=Surface + 1**: Clutter (Mugs, Bottles).
