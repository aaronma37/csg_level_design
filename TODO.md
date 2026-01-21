# TODO - Tile-Based Level Design

## High Priority: Foundation
- [x] Establish 32x32 Grid Standard.
- [x] Update Renderer (love_exp) to support grid-based tile assembly.
- [x] Create core tile set: `floor_wood_32`, `block_wood_32`, `pillar_stone_32`.
- [ ] Implement "Slope" metadata handling in renderer (for vertical traversal).
- [ ] Create `tools/tile_validator.py` to check for missing assets or invalid metadata.
- [ ] **Tech Debt & Refactoring**:
    - [x] Improve `procedural_gen.py` Mega-Tile reservation logic (read `block_size` from registry).
    - [x] Convert `collection_fireplace_nook` to a proper Mega-Tile Base Asset (`fireplace_mega_base`).

## Tile Sets to Build
- [ ] **Tavern Set** (In Progress):
    - [ ] Bar Counter (Straight/Corner)
    - [ ] Dining Set (Table + Chairs)
    - [ ] Fireplace Nook (with rug and armchair)
    - [ ] Wall segments (North/East variants with windows)

## Feature Polish
- [ ] Update `scene_view.lua` to support light params defined within tile files.

## Phase 3: Semantic Procedural Generation
- [x] **Audit & Tagging**:
    - [x] Add `tags` to all Asset JSON files in `csg/` (Initial pass via audit_tags.py).
    - [x] Add `tags` to all Tile Lua files in `csg_assets/tiles/` (via tile_registry.json).
- [ ] **Generator Infrastructure**:
    - [x] Create `tools/tile_registry.py` to index and query tiles by tags.
    - [x] Implement Phase 1: Connectivity solver (N/W wall doors).
    - [x] Implement Phase 2: Walkability path protector.
    - [ ] Implement Phase 3: WFC/Random-Fill populate (Basic random fill implemented, WFC pending).
- [ ] **Validation**:
    - [ ] Create `tactical_procedural_test.lua` to demonstrate the multi-phase gen.

## Deprecated/Retired
- [x] ASCII Map communication (superseded by Tile Grid).
- [x] 80x80 Grid (too large for character scale).
- [x] 64x64 Grid (too large for character scale).
- [x] Monolithic `tavern_layout.json` format.
