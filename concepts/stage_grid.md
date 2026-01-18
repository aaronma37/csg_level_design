# The Stage Grid System (5x4)

This standard defines a 5x4 ASCII-referenced grid for communicating layout composition.

## 1. The Grid Map (5x4)
We reference the 20 sectors using letters **A-T**.

```
          North (Back)
+---+---+---+---+---+
| A | B | C | D | E |  <- Backdrop / Skybox
+---+---+---+---+---+
| F | G | H | I | J |  <- Mid-Ground (Architecture)
+---+---+---+---+---+
| K | L | M | N | O |  <- The Stage (Characters, High Detail)
+---+---+---+---+---+
| P | Q | R | S | T |  <- Foreground (Camera, Framing)
+---+---+---+---+---+
          South (Front)
```

## 2. Sector Dimensions
*   **Total Grid:** 5x4 Cells.
*   **Cell Size:** Standard **80x80** voxels.
*   **Total Scene:** **400x320** voxels.

## 3. Directional Lighting
*   **Default Sun Direction:** `x = 0.33, y = -0.39, z = 0.29`

## 4. Sector Roles
*   **Q (Anchor):** Primary Camera location.
*   **L, M, N:** The Action Center (Stage).
*   **G, H, I:** Primary architectural backings.