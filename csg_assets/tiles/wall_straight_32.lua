return {
    name = "Timber Wall Straight (32x32)",
    size = {32, 32},
    metadata = { 
        tags = {"wall", "indoor", "wood"},
        nav_mask = 0
    },
    layout = {
        -- Floor (Anchor)
        { id = 'floor', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        
        -- Wall (Snap Back to Floor North Outer)
        -- Floor North Outer: Y = -20.
        -- Wall Back: Y = 12. Rot 180 -> -12.
        -- Offset: -20 - (-12) = -8.
        -- Result Pos: {0, -8, 0}. (Straddle).
        { asset_id = 'timber_wall_32', snap_to = 'floor.north_outer', snap_from = 'back', rot = 180 }
    }
}