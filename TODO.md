# Project Todo List

## Tooling & Pipeline
- [x] **Build `tools/check_layout_collisions.py` (The Layout Linter)**
- [ ] **Implement Debug Render Mode ("Clown Pass")**
    - **Why:** To solve "brown-on-brown" ambiguity. Textured images hide geometry errors.
    - **How:** Add a `--debug` flag to `previewer/main.lua`. When active, render objects with unique, high-contrast flat colors (based on Asset ID or Instance ID) instead of textures. This makes clipping and gaps visually obvious.

## Asset Generation
- [ ] **Fix Tavern Wall Corners**
    - **Issue:** Walls meeting at 90 degrees leave a visible gap or misalignment.
    - **Fix:** Update `generate_tavern_layout.py` to place a `timber_beam` or `stone_pillar` at the corners to physically hide the joint.

## Scene Polish
- [ ] **Refine "Jitter" Logic**
    - **Issue:** Random rotation sometimes pushes items off surfaces or into walls.
    - **Fix:** Use the Linter (once built) to "unit test" layouts and regenerate seeds until a collision-free layout is found.

## Sprite to Animated 3D Model Pipeline
- [x] **Phase 0: Planning & Documentation**
    - Created `concepts/sprite_to_3d_pipeline.md` and updated `WORKFLOWS.md`.
- [x] **Phase 1: Schema Definition (Blueprints)**
    - Implement Skeleton Library and Primitive definitions.
- [x] **Phase 2: Volumetric Generation & Painting**
    - Implement mass generation and surface projection logic.
- [x] **Phase 3: Validation & Iteration**
    - Build automated linter and previewer integration.
- [x] **Phase 4: Rigging & Data Preparation**
    - Implement voxel data structures with bone weights and physics props.
- [/] **Phase 5: Animation & Baking (IN PROGRESS)**
    - Implement skeletal animation engine and grid snapping (Done).
    - Bake 8-frame Walk Cycle (Done in `output/walk_cycle`).
    - **Current Stop Point:** Working on `previewer/main.lua` to view sequences. Note: Previewer currently has some camera control bugs that need reverting/fixing.
- [ ] **Phase 6: Optimization (Stretch)**
    - Implement `.vxb` format and LZ4 compression.

