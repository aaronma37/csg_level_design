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
*   **Modular Walls**: Walls should be designed as 32-unit segments.

## 5. The Baked-Tile Standard (Base Assets)
To ensure perfect alignment and eliminate runtime composition errors (floating walls, gap seams), we use a **Baked Base Asset** workflow.

*   **The Golden Rule**: Every Tile (`.lua`) must contain **exactly one** `base` asset.
    *   This asset physically contains the floor and the primary structure (e.g., Wall, Pillar, Bar Counter) combined into a single voxel model.
    *   **No Runtime Glues**: The engine does not glue a "Wall" to a "Floor". It renders one solid "WallTile" model.
*   **Asset Construction**:
    *   Generators should import a shared primitive (e.g., `floor_base_32`) to ensure the floor section is identical across all base assets.
    *   The structure is "baked" onto this floor during the generation phase (Python), not the compilation phase.

## 6. Tile Hierarchy
*   **Level 0: Substrates** (`generators/floors/`) - Voxel logic for floor patterns (Wood, Grass).
*   **Level 1: Baked Base Assets** (`wall_stone_grass_32.gltf`) - A monolithic unit mashing a feature onto a substrate. Must have `asset_tags = {"base"}`.
*   **Level 2: Tiles** (`wall_stone_32.lua`) - A wrapper around the Base Asset that adds metadata and Props.
*   **Level 3: Scenes** - A grid of Tiles.

## 7. Sockets & Props
Instead of gluing "Tiles" together, we attach "Props" (decorations) to **Sockets** on the Base Asset.

*   **Sockets**: Defined as `snap_points` in the Base Asset's JSON (e.g., `mantle_left`, `counter_top`).
*   **Props**: Small, non-base assets (candles, mugs) placed by the Tile definition.
*   **Compiler Logic**: The Tile Compiler resolves the Prop's position by looking up the Socket's coordinate in the Base Asset.
    *   *Lua Example*: `{ asset_id = 'candle', snap_to = 'base.mantle_left' }`

## 8. Mega Base Assets
For assets larger than 32x32 (e.g., a 2x1 Bar Counter):
*   The asset itself is a single large model (e.g., 64x32 voxels).
*   It is still the "Base Asset" for the multi-tile group.
*   The Scene places this Base Asset at the origin of the primary tile.


## 9. Gotchas & Best Practices
*   **Rotation Center**: Rotation happens around the asset's (0,0,0) center. 
    *   *Gotcha*: Rotating an offset wall (e.g., at X=16) 180 degrees moves it to X=-16. Always verify positions after rotation.
*   **Edge Alignment**: Walls often need to be inset to align with the *outer edge* of a floor tile.
    *   *Calculation*: `Tile_Edge (16)` - `Wall_Offset` = `Final_Pos`.
    *   *Fix*: Use **Snap Points** (Section 8) to align "Wall Back" to "Floor Edge".
*   **Scene Layering**: Scene generation occurs *after* Tile definition. You can override tile properties (like `tile_id`) dynamically in the scene loop (e.g., replacing edges with walls).
*   **Directional Tiles**: Create specific "wrapper" tiles for walls (e.g., `wall_north_32`, `wall_west_32`) that handle the internal rotation/positioning of the raw asset. This keeps the Scene file clean.