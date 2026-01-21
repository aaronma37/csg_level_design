return {
    name = "Bar Corner NW (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tile_tags = {"furniture", "bar", "corner", "clutter"} },
    lights = {
        { position = {0, 28, 45}, color = {1.0, 0.7, 0.3}, intensity = 100 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'bar_corner_64', pos = {0, 0, 0}, rot = 0 },
        -- Candle and mugs on the corner
        { asset_id = 'candles', pos = {-24, 24, 38}, rot = 0 },
        { asset_id = 'mug', pos = {-10, 24, 38}, rot = 45 }
    }
}
