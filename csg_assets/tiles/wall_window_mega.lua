return {
    name = "Timber Wall Window Mega (2x1)",
    size = {32, 32},
    metadata = { 
        tags = {"wall", "window", "mega"},
        nav_mask = 0,
        block_size = {2, 1}
    },
    layout = {
        { id = 'f1', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { id = 'f2', asset_id = 'floor_bevel_32', pos = {32, 0, 0}, rot = 0 },
        
        -- Window Slot (Rot 180)
        -- We want to span the two tiles.
        -- Center X of 2 tiles is 16.
        -- Floor 1 Center 0. Floor 2 Center 32.
        -- Slot Geometry `[0, 64]`. Rot 180 `[-64, 0]`.
        -- If we snap Front (Y=0?) to Floor North (Y=-16).
        -- We need to handle X centering.
        -- Slot "Center" is at 32? (If geometry 0..64).
        -- Let's check timber_wall_window_slot snap points.
        -- I didn't add snap points to it!
        -- I need to add snap points to `timber_wall_window_slot.json`.
        -- Center at `[32, 6, 0]`? (Width 64, Depth 12).
        -- Front at `[32, 0, 0]`.
        -- Back at `[32, 12, 0]`.
        
        -- Assuming I add those snaps:
        -- Snap `front` to `f1.north`?
        -- f1.north is `[0, -16, 0]`.
        -- Slot front `[32, 0, 0]`. Rot 180 -> `[-32, 0, 0]`.
        -- Offset: `Target [0, -16] - Source [-32, 0] = [32, -16]`.
        -- Pos = `[32, -16]`.
        -- This matches my manual calculation!
        
        { asset_id = 'timber_wall_window_slot', snap_to = 'f1.north', snap_from = 'front', rot = 180 },
        
        -- Window Glass
        -- Snap Center to Slot Center?
        -- `window_64` snaps (Need to add).
        -- Center `[0, 0, 0]` (Geometry `[-10, 10]`).
        -- Slot Center `[32, 6, 0]`.
        -- Rot 180 Slot Center -> `[-32, -6, 0]`.
        -- Target: `Pos[32, -16] + Rel[-32, -6] = [0, -22]`.
        -- Wait. Wall Center Y=6. Back=12. Front=0.
        -- If Front aligns to -16. Center aligns to -22?
        -- Front (0) -> -16.
        -- Center (6) -> -16 - 6 = -22.
        -- Back (12) -> -16 - 12 = -28.
        -- This puts window DEEP inside wall (at center depth).
        -- We probably want Glass Center aligned to Wall Center?
        -- Or aligned to a specific depth.
        -- Let's just assume simple centering for now.
        -- I need to add snaps to `window_64` too.
    }
}