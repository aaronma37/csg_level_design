# Semantic Procedural Generation (Phase 3 Roadmap)

## 1. Core Objectives
Transition from hardcoded coordinate loops to a semantic, multi-phase generation system that obeys room constraints, ensures walkability, and populates detail via a tagged tile/asset registry.

## 2. Generation Phases

### Phase 1: Constraint & Connectivity (Skeleton)
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
- Ensure a valid, walkable path exists from the South Entrance to all active Exits.
- Use `nav_mask` and `base_height` metadata from the Tile Registry to validate the path.
- Reserve path cells to prevent Phase 3 from placing blocking furniture.

### Phase 3: Semantic Filling (The Polish)
- Use **Wavefunction Collapse (WFC)** or a **Random Walk** to fill non-path cells.
- **Tile Selection**: Query the Tile Registry using tags (e.g., `indoor`, `wood`, `habitable`).
- **Collection Composition**: Populate tiles with asset collections (Level 1) using semantic tags:
    - *Example*: A tile tagged `social` can pull from the `Dining Set` collection.
    - *Example*: Assets tagged `clutter` are placed on surfaces tagged `tabletop`.

## 3. Data Requirements (The Audit)
- **Asset Tags**: Every `.json` in `csg/` needs an `asset_tags` field (e.g., `seating`, `table`, `storage`, `clutter`).
- **Tile Tags**: Every `.lua` in `csg_assets/tiles/` needs a `tile_tags` field (e.g., `floor`, `wall`, `doorway`, `transition`).
- **Tile Registry**: A central registry (or filtered filesystem view) that the generator can query by tag.

## 4. Input Schema (Proposed)
```json
{
  "theme": "tavern",
  "connectivity": {
    "north": true,
    "west": false
  },
  "constraints": {
    "min_size": [8, 8],
    "max_size": [16, 16]
  }
}
```
