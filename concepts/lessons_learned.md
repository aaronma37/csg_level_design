# Lessons Learned: Neuro-Symbolic Voxel Design

## 1. Tooling & Workflow
- **VoxelBuilder (Logical Placement):** For assets under 16x16 or modular props, procedural logic (loops, `fill`, `carve`, `mirror_x`) is superior to string-based slicing. It is more readable for LLMs and produces cleaner geometry.
- **Layout Engine (Center-Point Logic):** Scene composition should always be defined by **Center Coordinates**. Using corner-based coordinates is error-prone for LLMs. The layout engine should handle the conversion based on a registered asset size.
- **Rotation-Aware Scaling:** When rotating assets 90° or 270°, the composer MUST swap the Width and Depth dimensions in the translation math to maintain alignment.

## 2. Technical Constraints
- **The 255-Voxel Limit:** Standard VOX chunks cannot exceed 255 voxels in any dimension. Large structures (floors, walls) must be modularized into segments (e.g., 160x160 tiles) and assembled in the layout.
- **Protected Palette:** Indices **100-149** are sacred. They are used for texture lookups in character reconstruction and must never be modified or truncated.

## 3. Visual & Aesthetic Standards
- **Ghost Emission:** To create volumetric light (window glow, magical auras), use indices **250-255** with **Alpha=0**. These are grouped into the Emissive mesh for bloom but don't create solid geometry.
- **Isometric Visibility:** Always build with a "Dollhouse" perspective. Avoid high structures on the South and West edges to prevent character occlusion from the fixed azimuth camera.
- **CU Alignment:** 
    - Seat Height: 0.25 CU (12-14v)
    - Counter Height: 0.7 - 0.8 CU (35-40v)
    - Stair Rise: 1.6 CU per floor (80v)

## 4. Tile Paradigm Shift (FFT-Style)
- **Grid Scale (32x32 Final Standard):** We iterated from 80x80 (too loose) to 64x64 (better), but finally settled on **32x32**. This scale provides the tightest tactical "density" where characters (50-70v tall) feel powerful and occupy the grid meaningfully. It also simplifies the "Baked Tile" generation math significantly.
- **ASCII Maps vs. Lua Tiles:** While ASCII is good for quick communication, it lacks the precision for 3D metadata (height, rotation). Pure Lua Tile definitions are more robust for defining collision, navigation, and lighting logic.
- **Tile-Internal Flooring:** Tiles that represent habitable areas should contain their own base floor geometry. This prevents Z-fighting and simplifies the high-level scene layout.

## 5. Asset Coordinates & Layouts (2026 Update)
- **Mega Tile Coordinates (Center-Relative):** 
  - Assets are defined relative to the **Center of the Primary (Top-Left) Tile** (Coordinate 0,0).
  - A Standard Tile (32x32) spans `X = -16` to `16`.
  - A 2x1 Mega Tile (64 Wide) spans `X = -16` to `48` (Width 64).
  - A 2x2 Mega Tile spans `X = -16` to `48` and `Y = -16` to `48`.
- **Prop Origins:** Standalone props (candles, books, barrels) should use a **Center-Bottom Origin** (X/Y=0, Z=0) to simplify placement on surfaces.
- **Snap Points & IDs:**
  - In Tile Lua definitions, `snap_to` references (e.g., `snap_to = 'base.spot'`) **REQUIRE** the target item to have an explicit `id` field (e.g., `{ id = 'base', ... }`). Without this, the snap fails silently.
- **CSG Compiler Limitations:**
  - `csg_compiler.py` does **NOT** support rotation (`rot`) within the JSON instructions. Rotations must be applied in the Tile Lua or by manually calculating voxel positions.
  - `cylinder` shape is supported and preferred over `point_cloud` for round objects.
- **Palette Authority:** `palette.py` is the source of truth for colors. Documentation (`material_system.md`) may be outdated.
  - **Metal:** Use **47** (Charcoal) or **23** (Stone Highlight) instead of 240 (which is Emissive Fire).