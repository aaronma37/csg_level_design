# Layout Standards & Conventions (Tile Paradigm)

## 1. Coordinate System (Scene Space)
*   **Vertical (Y-Up)**: 1 Unit = 1 Voxel. Height is stored in the Y component.
*   **Horizontal (X, Z)**: The ground plane.
    *   **X Axis**: West (-X) to East (+X).
    *   **Z Axis**: North (-Z) to South (+Z).
    *   **Camera Configuration**: Defined by orbit parameters relative to a target `center` {x, y, z}.
        *   **Do NOT use 'eye' position.**
        *   **distance**: Distance from the center. Standard is **500**.
        *   **angle**: Horizontal rotation (azimuth). Standard is **45 degrees** (0.785 radians).
        *   **height**: Vertical offset from the center plane. Standard is **300**.
        *   **fov**: Field of View. Standard is **40**.
*   **The Grid**: Standard Tiles are **32x32** voxels on the X/Z plane.
*   **Normal Layout Size**: 16x16 tiles (512x512 voxels total).
*   **Scene Grid**: Positions in scene files are expressed as grid indices `{x, z}` (or `{x, z, y}` for elevation).
*   **Asset Mismatch**: Raw CSG assets are typically authored as **Z-Up**. They must be rotated (usually -90 deg on X) to align with the Scene's Y-Up system.

## 2. Tile Architecture
Every tile is a 32x32 "slice" of the map. 
*   **Self-Contained**: Tiles should generally include their own floor asset (`floor_bevel_32`) if they represent a walkable or solid area.
*   **Mega-Tiles**: Large furniture (Tables, Bars) that cannot fit on a 32x32 footprint are defined as "Mega-Tiles" that occupy multiple grid cells (e.g., 2x1 or 2x2).
    *   **CRITICAL**: Mega-Tiles must define `size = {32, 32}` to align with the map grid, even if they visually span larger areas. Use `block_size` for logical occupancy.
*   **Height Tiers**: Standard elevation increments are **16 units**.
    *   Tier 0: Y=0
    *   Tier 1: Y=16
    *   Tier 2: Y=32
*   **Metadata**:
    *   `base_height`: The elevation for character navigation.
    *   `height_type`: `flat` or `slope`.
    *   `nav_mask`: `1` for walkable, `0` for blocked.

## 3. Anchors & Pivots
*   **Tiles**: Anchored at their top-left corner relative to the grid cell.
*   **Assets (.json/.vox)**: 
    *   **Center-Zero Rule**: All assets must be centered at `(0, 0)` in X and Y (Asset Space).
    *   **Floor-Alignment**: The bottom of the asset should align with 0 on the vertical axis.
    *   Run `python3 tools/normalize_asset.py <asset>` to enforce this.
    *   **Snap Points**: Use `snap_points` in the asset definition for precise alignment (see Section 8).

## 4. Dollhouse Strategy (Visibility)
Since the camera is fixed at a **South-East** perspective (looking North-West):
*   **North (-Z) & West (-X) Edges**: These are the "Back Walls". Use these for tall structures, windows, and high shelving. They form the visible backdrop.
*   **South (+Z) & East (+X) Edges**: These are the "Foreground". Keep these clear or use low-profile "cutaway" assets to prevent blocking the view of the play area.
*   **Modular Walls**: Walls should be designed as 32-unit segments that can be swapped into a tile's `layout`.

## 5. Tile Hierarchy
*   **Level 0: Assets** (`floor_bevel_32.gltf`, `chair.gltf`) - The raw geometry.
*   **Level 1: Tiles** (`floor_wood_32.lua`, `dining_table_mega.lua`) - Combinations of assets + navigation metadata.
*   **Level 2: Scenes** (`tavern_grid.lua`) - A collection of tiles arranged on the global grid.

## 6. Vertical Stacking (Y-Axis)
*   **Y=0**: Sub-floor/Backing.
*   **Y=1**: Surface planks/Tile top.
*   **Y=2**: Furniture base contact.
*   **Y=Surface + 1**: Clutter (Mugs, Bottles).

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

## 8. Anchors & Snapping (The Compiler Paradigm)
To solve alignment issues (e.g., flushing walls to tile edges), use the Anchor System resolved by `tile_compiler.py`:

*   **Snap Points**: Defined in Asset JSON (`.json`) under `snap_points`.
    *   **Standard**: `north` (-16), `south` (16), `east` (16), `west` (-16) for tiles.
    *   **Wall Standard**: `front` (0), `back` (12) for walls.
*   **Workflow**:
    1.  Source Lua: `{ id = 'w1', snap_to = 'floor.north', snap_from = 'front' }`.
    2.  Build Step: `tile_compiler.py` runs during `./deploy_assets.sh`.
    3.  Math: `Final_Pos = Target_Anchor_World_Pos - Source_Anchor_Local_Rotated_Offset`.
    4.  Output Lua: `{ id = 'w1', pos = {0, -16, 0} }`.
*   **Result**: Semantic positioning in source files, explicit performance in the engine.

## 9. Gotchas & Best Practices
*   **Rotation Center**: Rotation happens around the asset's (0,0,0) center. 
    *   *Gotcha*: Rotating an offset wall (e.g., at X=16) 180 degrees moves it to X=-16. Always verify positions after rotation.
*   **Edge Alignment**: Walls often need to be inset to align with the *outer edge* of a floor tile.
    *   *Calculation*: `Tile_Edge (16)` - `Wall_Offset` = `Final_Pos`.
    *   *Fix*: Use **Snap Points** (Section 8) to align "Wall Back" to "Floor Edge".
*   **Scene Layering**: Scene generation occurs *after* Tile definition. You can override tile properties (like `tile_id`) dynamically in the scene loop (e.g., replacing edges with walls).
*   **Directional Tiles**: Create specific "wrapper" tiles for walls (e.g., `wall_north_32`, `wall_west_32`) that handle the internal rotation/positioning of the raw asset. This keeps the Scene file clean.