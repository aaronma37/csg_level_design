# Voxel Style Guide

## 1. Scale & Resolution
- **Standard Tile:** 32x32 voxels (Composition Unit).
- **Standard Character:** 55-65 voxels tall.
- **Doorways:** 70 voxels tall.
- **Furniture Scale:** 1 unit = 1 voxel. A standard chair seat should be ~10-12 voxels high.

- **Aesthetic Rules:**
    - **The 16-Voxel Rule:** Assets smaller than 16x16x16 voxels should avoid SDF/CSG sampling. Instead, use the **VoxelBuilder** workflow (Logical Placement) to ensure pixel-perfect readability and sharp silhouettes.
    - **Materiality:** Every asset must strictly use indices from `palette.py` to ensure lighting and shaders react correctly in-engine.
- **Density:** Favor "chunky" silhouettes. Avoid "stair-stepping" on diagonals unless it serves a specific texture (like a cracked wall).
- **Detailing:** Use the "Small/Medium/Large" rule:
    - **Large:** Overall silhouette (e.g., the cone of a robe).
    - **Medium:** Functional parts (e.g., sleeves, sash).
    - **Small:** "Magic" particles, gold trim, or eye-recesses.

## 4. Semantic Anchoring (The Scale Ruler)
To ensure the world feels cohesive, all assets are sized relative to the **Standard Character**.

- **CHARACTER UNIT (1.0 CU):** ~50-60 voxels. This is the primary anchor.
- **WAIST HEIGHT (0.5 CU):** ~25-30 voxels. 
    - *Example:* The **Medieval Feast Table** (top surface) is anchored at 25 voxels.
- **KNEE HEIGHT (0.25 CU):** ~12-15 voxels.
    - *Example:* Chair seats, benches, small crates.
- **OVERHEAD (1.2 CU+):** 70+ voxels.
    - *Example:* Door frames (70v), Ceilings (90v+), Fireplace Mantels (often 0.6 CU or 35v).

## 5. Verification Checklist
When creating a new asset generator, ask:
## 6. Lighting & Emitters
To enable the **Auto-Lighting System**, assets that emit light (candles, fireplaces, magic runes) should define `light_emitters` in their JSON metadata.

*   **Structure**:
    ```json
    "light_emitters": [
      {
        "offset": [0, 0, 5],      // Position relative to asset origin (before rotation)
        "color": [1.0, 0.9, 0.6], // RGB normalized (0.0 - 1.0)
        "intensity": 40           // Radius/Brightness factor
      }
    ]
    ```
*   **Behavior**: The `tile_compiler.py` will automatically transform these offsets based on the prop's final position and rotation in the Tile, adding them to the Scene's light list.

