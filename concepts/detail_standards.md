# Visual Density Standards

To prevent the "Big Boring Block" effect, all assets must adhere to the **Rule of Three Levels of Detail**.

## 1. The Three Levels
1.  **Macro (The Silhouette):** The basic shape (e.g., "A House"). Visible from far away.
2.  **Meso (The Structural Detail):** Windows, door frames, support beams, roof overhangs. These should occur at least every **0.5 CU**.
3.  **Micro (The Texture):** Individual bricks, wood grain, cracks, or color jitter. These should occur every **1-2 voxels**.

## 2. Density Metric: FD (Feature Density)
**FD = Number of visual "breaks" per 1.0 CU (50 voxels).**

| Asset Type | Target FD | Strategy |
|------------|-----------|----------|
| **Structural** (Walls, Floors) | 4 - 6 | Use patterns (bricks/planks) or trim-strips. |
| **Furniture** (Tables, Chairs) | 8 - 12 | Use chamfered edges, leg-tapering, and grain. |
| **Hero Assets** (Characters, Magic) | 15+ | Manual carving, emissive highlights. |

## 3. The "Anti-Block" Rule
Any flat surface larger than **0.4 CU x 0.4 CU** (20x20 voxels) MUST be broken up by a Meso or Micro detail.
