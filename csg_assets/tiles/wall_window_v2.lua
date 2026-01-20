return {
    name = "Timber Window Wall V2 (32x32)",
    size = {32, 32},
    metadata = { tile_tags = {"wall", "north", "window", "v2"}, nav_mask = 0 },
    layout = {
        { id = 'f', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'wall_window_v2', snap_to = 'f.north', snap_from = 'front', rot = 180 }
    }
}
