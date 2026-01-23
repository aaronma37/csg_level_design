return {
    name = "Tavern Door Mega (3x1)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 1,
        tile_tags = {"wood", "tavern", "door", "mega"},
        block_size = {3, 1}
    },
    layout = {
        { asset_id = 'tavern_door_mega_3x1', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'candles', snap_to = 'tavern_door_mega_3x1.candle_left', rot = 0 },
        { asset_id = 'candles', snap_to = 'tavern_door_mega_3x1.candle_right', rot = 0 }
    }
}