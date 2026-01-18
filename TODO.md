# TODO - Tile-Based Level Design

## High Priority: Foundation
- [x] Establish 64x64 Grid Standard.
- [x] Update Renderer (love_exp) to support grid-based tile assembly.
- [x] Create core tile set: `floor_wood_64`, `block_wood_64`, `pillar_stone_64`.
- [ ] Implement "Slope" metadata handling in renderer (for vertical traversal).
- [ ] Create `tools/tile_validator.py` to check for missing assets or invalid metadata.

## Tile Sets to Build
- [ ] **Tavern Set**:
    - [ ] Bar Counter (Straight/Corner)
    - [ ] Dining Set (Table + Chairs)
    - [ ] Fireplace Nook (with rug and armchair)
    - [ ] Wall segments (North/East variants with windows)
- [ ] **Nature Set**:
    - [ ] Grass/Dirt transition
    - [ ] Water/River tiles
    - [ ] Trees and Large Rocks

## Feature Polish
- [ ] Update `scene_view.lua` to support light params defined within tile files.
- [ ] Implement rotation logic for tiles (ensure metadata like `slope_dir` rotates correctly).
- [ ] Add "Prop" support to tiles (allowing random clutter based on tags).

## Deprecated/Retired
- [x] ASCII Map communication (superseded by Tile Grid).
- [x] 80x80 Grid (too large for character scale).
- [x] Monolithic `tavern_layout.json` format.
