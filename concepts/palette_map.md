# Material Palette Map

This document maps `palette.py` indices to their intended physical materials.

| Range | Material | Description |
|-------|----------|-------------|
| 1-20  | **Wood** | 1-5: Dark/Old, 6-10: Pine/New, 11-20: Painted/Special. |
| 21-40 | **Stone**| 21-30: Grey Cobble, 31-40: Smooth/Sandstone. |
| 41-60 | **Flesh/Organic** | 44: Standard Skin, 45: Skin Shadow. |
| 61-100| **Fabric** | Primary colors for clothing and banners. |
| 240-255| **Emissive** | 240-245: Gold/Metal (High spec), 250-255: Magic (Glow). |

**Note:** The `vox_to_gltf.py` exporter treats indices 240+ as having an emissive material layer.
