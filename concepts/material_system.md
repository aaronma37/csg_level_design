# Neuro-Symbolic Material System

This system defines how **Voxel Indices** map to **Shader Properties**. Instead of manually painting lighting, we use semantic indices that the game engine interprets as physical materials.

## 1. Material Mapping (Logic Table)

| Index Range | Material Name | Metallic | Roughness | Emissive | Description |
|-------------|---------------|----------|-----------|----------|-------------|
| 1 - 20      | **Wood**      | 0.0      | 0.8       | 0.0      | Matte, organic grain. |
| 21 - 40     | **Stone**     | 0.0      | 0.9       | 0.0      | Highly diffuse, rough. |
| 41 - 99     | **Fabric**    | 0.0      | 1.0       | 0.0      | Absolute matte, absorbs light. |
| 100 - 149   | **Flesh**     | 0.0      | 0.5       | 0.0      | Subsurface-like softness. |
| 240 - 245   | **Metal**     | 1.0      | 0.2       | 0.1      | Shiny, reflective gold/iron. |
| 250 - 255   | **Magic**     | 0.0      | 0.0       | 1.0      | Pure light source. |

## 2. In-Engine Interpretation
The `vox_to_gltf.py` script automatically splits the voxel mesh into sub-meshes based on these ranges.
- **Range 0-239:** Rendered with the `Standard` PBR shader.
- **Range 240-255:** Rendered with the `Emissive` Bloom shader.

## 3. The Detail Strategy
- **Micro-Detail (Surface):** Should be handled by the **Shader**. For example, the shader can apply a noise-texture to the "Stone" range to simulate grit without adding extra voxels.
- **Meso-Detail (Structure):** Should be handled by the **CSG Generator**. If you want a "carved" look on a pillar, the generator must physically subtract a cylinder or sphere.
