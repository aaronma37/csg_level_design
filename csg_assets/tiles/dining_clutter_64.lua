return {
    name = "Cluttered Dining Set (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"furniture", "table", "clutter"} },
    lights = {
        { position = {0, 28, 0}, color = {1.0, 0.7, 0.3}, intensity = 80 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'medieval_feast_table', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'chair', pos = {0, 20, 0}, rot = 0 },
        { asset_id = 'chair', pos = {0, -20, 0}, rot = 180 },
        -- Clutter
        { asset_id = 'mug', pos = {-12, 8, 25}, rot = 45 },
        { asset_id = 'mug', pos = {15, -6, 25}, rot = 120 },
        { asset_id = 'candles', pos = {0, 0, 25}, rot = 0 }
    }
}
