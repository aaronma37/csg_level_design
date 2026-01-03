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
