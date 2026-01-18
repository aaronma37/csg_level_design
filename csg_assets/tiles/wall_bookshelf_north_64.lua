return {
    name = "Wall Bookshelf North (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "north", "furniture", "books", "clutter"} },
    lights = {
        { position = {0, 18, 85}, color = {1.0, 0.7, 0.3}, intensity = 60 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {0, 28, 0}, rot = 0 },
        { asset_id = 'stocked_shelf_64', pos = {0, 18, 0}, rot = 0 },
        -- Candles on top (shelf height is 80)
        { asset_id = 'candles', pos = {0, 18, 80}, rot = 0 }
    }
}
