# Layout Standards & Conventions

## 1. Coordinate System
*   **Z-Up:** Z is the vertical axis (Height).
*   **Units:** 1 Unit = 1 Voxel.
*   **Grid:** Standard tiles are typically 16x16 or 32x32.

## 2. Anchors (Pivot Points)
*   **Furniture:** Anchored at **(0,0,0)**, which corresponds to the **Bottom-Center** or **Bottom-Back** depending on the object type.
    *   *Symmetrical (Tables, Chairs):* Bottom-Center.
    *   *Directional (Bars, Cabinets):* Bottom-Back-Center (The "Back" is on the Anchor, the object extends Forward into +Y).
*   **Walls:** Anchored at the Bottom-Back-Left corner of the segment.

## 3. Orientation (The Forward Manifesto)
*   **Default Forward:** **Positive Y (+Y)**.
*   **Standard Rotations (Euclidean):**
    *   **Rot 0:** Faces **South** (Extends into +Y).
    *   **Rot 90:** Faces **West** (Extends into -X).
    *   **Rot 180:** Faces **North** (Extends into -Y).
    *   **Rot 270:** Faces **East** (Extends into +X).
*   *Note:* In the "Dollhouse" view, North and East are the "Back" walls.

## 4. Snap Points
*   **Usage:** Use `snap_to` in layouts to attach objects to defined slots on parent assets.
*   **Inheritance:** Snap points inherit the parent's global rotation and position automatically.
*   **Naming Standards:**
    *   `seat_1..N`: For chairs around tables or bars.
    *   `top_left`, `top_center`, `top_right`: For clutter on surfaces.
    *   `mantle_left`, `mantle_right`: Specific to fireplaces.
    *   `window_mount`, `door_mount`: For structural openings in slotted walls.
    *   `next_segment`, `corner_turn`: For chaining structural assets (walls, railings).

## 5. Collection Hierarchy (The Lego approach)
*   **Level 0: Leaf Asset** (`chair.json`) - Raw CSG geometry.
*   **Level 1: Sub-Collection** (`collection_dining_snapped.json`) - A table + its snapped chairs.
*   **Level 2: Zone Collection** (`collection_dining_hall.json`) - Multiple dining sets + chandeliers.
*   **Level 3: Layout** (`tavern_layout.json`) - The final assembly of all zones and the shell.

## 6. Dollhouse Strategy (Visibility)
*   **Isometric Visibility:** Camera is fixed at South-West looking North-East.
*   **The Rule:** Avoid high structures (tall walls, pillars, high shelves) on the **South (Y=0)** and **West (X=0)** edges.
*   **Structural Implementation:**
    *   **North/East Walls:** Full height (140 units), slotted for windows/doors.
    *   **South/West Walls:** Cut away (Empty or low-profile floor trim).
    *   **Tall Props:** Fireplaces and bookshelves MUST be snapped to North/East walls.

## 7. Voxel-Clean Pass (Z-Stacking)
To prevent flickering (Z-fighting) and linter collisions, use standard vertical offsets:
*   **Z=0:** Floor plane only.
*   **Z=1:** Large flat items (Rugs, Floor-mounted railings).
*   **Z=2:** Primary furniture bases (Table legs, Chair legs, Bar base).
*   **Z=TableHeight + 1:** Props sitting on surfaces (Mugs, Bottles).
*   **Z=80+:** Mezzanine level structural elements.
