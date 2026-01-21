return {
    name = "Bar Counter North (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tile_tags = {"furniture", "bar", "north", "clutter"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'bar_straight_64', pos = {0, 20, 0}, rot = 0 },
        -- Mugs on counter (height 38)
        { asset_id = 'mug', pos = {-15, 25, 38}, rot = 15 },
        { asset_id = 'mug', pos = {10, 22, 38}, rot = 110 }
    }
}
