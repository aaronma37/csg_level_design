return {
    name = "Timber Wall V2 (32x32)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"wall", "north", "indoor", "wood", "v2"},
        nav_mask = 0
    },
    layout = {
        { id = 'floor', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Align the tile_snap anchor of the wall to the north edge of the floor
        { asset_id = 'timber_wall_v2', snap_to = 'floor.north', snap_from = 'front', rot = 180 }
    }
}
