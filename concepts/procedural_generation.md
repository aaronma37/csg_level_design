# Semantic Procedural Generation

## 1. Core Objectives
Transition from hardcoded coordinate loops to a semantic, multi-phase generation system that obeys room constraints, ensures walkability, and populates detail via a tagged tile/asset registry.

**Active Tool**: `tools/procedural_gen.py`

## 2. Generation Phases (Implemented)

### Phase 1: Constraint & Connectivity (Skeleton)
*Implemented in `generate_room`*
- **Stability Rules**:
    - **Pool Filtering**: Queries for backdrop walls MUST exclude functional tags like `doorway`, `fireplace`, or `mega`.
    - **Corner Awareness**: The Northwest corner (0,0) must use a tile explicitly tagged `corner`.
    - **Single Exit Rule**: Only one doorway tile per requested path direction.
- **Entrance**: Always assumed on the **South** edge.
- **Exits**: Restricted to **North** and **West** walls (to respect Dollhouse visibility constraints).
- **Paths**: Next-room paths are input as `north=bool`, `west=bool`.
- **Wall Logic**:
    - North Wall: Contains a door if `north=true`, otherwise solid/window.
    - West Wall: Contains a door if `west=true`, otherwise solid/window.
    - South/East Edges: Generally kept clear or use low-profile cutaways.

### Phase 2: Navigation & Flow (Pathfinding)
*Implemented in `get_path`*
- Ensure a valid, walkable path exists from the South Entrance to all active Exits.
- Use `nav_mask` and `base_height` metadata from the Tile Registry to validate the path.
- Reserve path cells to prevent Phase 3 from placing blocking furniture.

### Phase 3: Semantic Filling (The Polish)
*Implemented via `initial_assets` and `random` filling*
- Use **Wavefunction Collapse (WFC)** or a **Random Walk** to fill non-path cells.
- **Tile Selection**: Query the Tile Registry using tags (e.g., `indoor`, `wood`, `habitable`).
- **Collection Composition**: Populate tiles with asset collections (Level 1) using semantic tags:
    - *Example*: A tile tagged `social` can pull from the `Dining Set` collection.
    - *Example*: Assets tagged `clutter` are placed on surfaces tagged `tabletop`.

## 3. Data Requirements (The Audit)
- **Asset Tags**: Every `.json` in `csg/` needs an `asset_tags` field (e.g., `seating`, `table`, `storage`, `clutter`).
- **Tile Tags**: Every `.lua` in `csg_assets/tiles/` needs a `tile_tags` field (e.g., `floor`, `wall`, `doorway`, `transition`).
- **Tile Registry**: A central registry (`csg_assets/tile_registry.json`) that the generator queries.

## 4. Theming System (Abstraction)
To allow the same algorithms to generate Taverns, Dungeons, or Forests, we decouple "Roles" from "Assets" using a **Theme Definition**.

The Generator queries the Theme for tags, rather than hardcoding "wood" or "stone".

### Theme Structure
A Theme defines the specific tags required to fulfill logical slots in the room:

| Role | Description | Tavern Example Tags |
| poss | ----------- | ------------------- |
| **`floor`** | Standard ground tile | `["floor", "wood"]` |
| **`wall_north`** | Backdrop wall segments | `["wall", "north", "interior"]` |
| **`corner_nw`** | The 0,0 corner piece | `["wall", "corner", "north"]` |
| **`door_north`** | North-facing exit | `["wall", "doorway", "north"]` |
| **`feature_main`** | Major focal point (Fireplace) | `["fireplace", "mega"]` |
| **`scatter`** | Random decor | `["clutter", "mug"]` |

## 5. Usage
```bash
python3 tools/procedural_gen.py --name "tavern_test" --width 12 --height 12 --north --west --theme tavern
```
