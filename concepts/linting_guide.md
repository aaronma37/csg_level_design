# Voxel Linting Guide

The layout linter (`tools/lint_layout.py`) is used to detect physical overlaps between assets. In a voxel-based world, two objects occupying the same coordinate results in visual glitches and structural ambiguity.

## 1. Running the Linter
Execute the tool against any layout JSON:
```bash
python3 tools/lint_layout.py csg/tavern_layout.json
```

## 2. Interpreting Results
The linter will output "ERROR: Found X overlapping voxels".

### Critical Collisions (Must Fix)
*   **Asset-Asset Clipping:** Chairs inside tables, walls overlapping each other.
*   **Floor-Furniture Clipping:** Legs submerged in the floor. 
    *   *Fix:* Use the **Z-Stacking** rule (Furniture at Z=2).

### Acceptable Overlaps (Logical Detail)
*   **Structural Slots:** Placing a `window` in a `timber_wall_window_slot` may show minor overlaps (under 100 voxels) if the hole isn't pixel-perfect.
*   **Rug-Furniture:** Chairs sitting on a rug will overlap by 1 voxel layer ($Z=1$ vs $Z=2$). This is often necessary for a "grounded" look but should be minimized.

## 3. Strategies for "Zero-Collision"
*   **Slotted Assets:** Instead of placing a window *inside* a solid wall, create a wall asset with a pre-carved hole.
*   **Snap Chaining:** Use the `next_segment` snap point on walls to ensure segments touch end-to-end without overlapping.
*   **The Air Gap:** When in doubt, leave a 1-voxel gap. In a 3D renderer, this is invisible but satisfies the linter.
*   **Manual Offsets:** If a collection's center is $(160, 160)$, and the wall is $12$ thick, the wall should be at $160 + 1 = 171$ to clear the boundary perfectly.
