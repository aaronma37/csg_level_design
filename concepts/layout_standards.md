# Layout Standards

To ensure optimal gameplay visibility from the fixed in-game perspective (210° Azimuth, -15° Elevation), all layouts must adhere to the following rules.

## 1. The Isometric Visibility Rule
The camera looks from the **South-West** toward the **North-East**.
- **Occlusion Hazard Zone:** Avoid placing high walls, large pillars, or tall furniture on the **South** (-Y) and **West** (-X) edges of the layout.
- **Backdrop Zone:** Place high walls and large background elements on the **North** (+Y) and **East** (+X) edges.
- **Height Limit:** Any structural element in the South/West foreground should not exceed **0.25 CU** (12-15 voxels) in height to avoid covering characters.

## 2. Dollhouse Wall Strategy
- **Visible Walls:** Only render the North and East walls to create a "Dollhouse" effect.
- **Corner Alignment:** Walls should perfectly align with the outer edges of the `wooden_floor` to prevent floating voxels or gaps.

## 3. Floor Alignment
- All static furniture (tables, rugs, racks) should be anchored at **Z=1** (immediately above the floor plane).
- Walls should be anchored at **Z=0** and sit flush against the floor's bounding box.
