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

