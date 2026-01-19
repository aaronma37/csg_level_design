# Layout Standards & Conventions (Tile Paradigm)

## 1. Coordinate System
*   **Vertical (Z-Up)**: 1 Unit = 1 Voxel.
*   **Horizontal (X, Y)**: 1 Unit = 1 Voxel.
*   **The Grid**: Standard Tiles are **32x32** voxels.
*   **Scene Grid**: Positions in scene files are expressed as grid indices `{x, y}` (e.g., `{0, 0}`, `{1, 0}`).

## 2. Tile Architecture
Every tile is a 32x32 "slice" of the map. 
*   **Self-Contained**: Tiles should generally include their own floor asset (`floor_bevel_32`) if they represent a walkable or solid area.
*   **Mega-Tiles**: Large furniture (Tables, Bars) that cannot fit on a 32x32 footprint are defined as "Mega-Tiles" that occupy multiple grid cells (e.g., 2x1 or 2x2).
    *   **CRITICAL**: Mega-Tiles must define `size = {32, 32}` to align with the map grid, even if they visually span larger areas. Use `block_size` for logical occupancy.
*   **Height Tiers**: Standard elevation increments are **16 units**.
    *   Tier 0: Z=0
    *   Tier 1: Z=16
    *   Tier 2: Z=32
*   **Metadata**:
    *   `base_height`: The elevation for character navigation.
    *   `height_type`: `flat` or `slope`.
    *   `nav_mask`: `1` for walkable, `0` for blocked.

## 3. Anchors & Pivots
*   **Tiles**: Anchored at their top-left corner relative to the grid cell.
*   **Assets (.json/.vox)**: 
    *   **Center-Zero Rule**: All assets must be centered at `(0, 0)` in X and Y.
    *   **Z-Floor Rule**: The bottom of the asset (Z-min) should be at `Z=0` (unless it's a ceiling fixture).
    *   Run `python3 tools/normalize_asset.py <asset>` to enforce this.

## 4. Dollhouse Strategy (Visibility)
Since the camera is fixed at a South-West perspective:
*   **North/East Edges**: Use these for tall structures (walls, pillars, high shelves).
*   **South/West Edges**: Keep clear or use low-profile "cutaway" assets.
*   **Modular Walls**: Walls should be designed as 32-unit segments that can be swapped into a tile's `layout`.

## 5. Tile Hierarchy
*   **Level 0: Assets** (`floor_bevel_32.gltf`, `chair.gltf`) - The raw geometry.
*   **Level 1: Tiles** (`floor_wood_32.lua`, `dining_table_mega.lua`) - Combinations of assets + navigation metadata.
*   **Level 2: Scenes** (`tavern_grid.lua`) - A collection of tiles arranged on the global grid.

## 6. Z-Stacking (Voxel-Clean Pass)
*   **Z=0**: Sub-floor/Backing.
*   **Z=1**: Surface planks/Tile top.
*   **Z=2**: Furniture base contact.
*   **Z=Surface + 1**: Clutter (Mugs, Bottles).

## 7. Mega Tile Positioning Standards
To ensure multi-tile assets (Mega Tiles) align correctly:

1.  **Grid-Lock**: In the Tile Definition (`.lua`), always set `size = {32, 32}`. This forces the scene loader to use the standard grid step.
2.  **Asset Origin**: Ensure the referenced asset is normalized (Centered X/Y at 0, Z at 0).
3.  **Layout Offset Formula**:
    *   To center an asset on a Mega Tile block (assuming Top-Left Anchor):
    *   **Offset X** = `(Total_Width_In_Voxels / 2)`
    *   **Offset Y** = `(Total_Depth_In_Voxels / 2)` (or align to wall as needed).
    
    *Example: 2x2 Mega Tile (64x64)*
    *   Asset Center: 0,0
    *   Layout Pos: `{32, 32, 0}`