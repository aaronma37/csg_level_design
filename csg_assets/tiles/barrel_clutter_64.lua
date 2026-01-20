return {
    name = "Barrel Clutter (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tile_tags = {"clutter", "barrels"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        -- A cluster of three barrels
        { asset_id = 'barrel', pos = {-10, -8, 0}, rot = 15 },
        { asset_id = 'barrel', pos = {12, -5, 0}, rot = 340 },
        { asset_id = 'barrel', pos = {2, 12, 0}, rot = 90 }
    }
}
