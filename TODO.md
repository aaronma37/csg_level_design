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

### Refactoring: Agnostic Asset Attachment System
- [ ] **1. Implement Online Transform Calculation**
    - Modify the animation loop to calculate bone transforms (Position + Rotation) *online*, immediately after the skeleton is drawn/updated.
    - Store these transforms in a table for the current frame.
    - **Constraint:** Derive transforms directly from the active joint positions (World Space), not bind poses.
    - **Orientation:** Ensure the calculated transform aligns such that an asset centered at (0,0,0) with +X forward points along the bone vector (Parent -> Child).
- [ ] **2. Visualize Transforms**
    - Implement a visualizer using simple elongated cubes (or debug lines) to verify the calculated transforms in real-time.
- [ ] **3. Create Agnostic Asset Generators**
    - Remove current modular asset generators.
    - Create new generators that are agnostic to the rig/skeleton.
    - Tag assets with the bone they associate with.
    - Define assets in their own local frame (pointing +X).
- [ ] **4. Integrate New Assets**
    - Swap the test visualization with these new agnostic assets.

- [ ] **Phase 6: Optimization (Stretch)**
    - Implement `.vxb` format and LZ4 compression.
