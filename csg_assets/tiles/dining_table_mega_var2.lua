return {
    name = "Dining Table Mega Var2 (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 2}
    },
    lights = {
        { position = {20, 25, 32}, color = {1.0, 0.7, 0.3}, intensity = 40 },
        { position = {44, 25, 32}, color = {1.0, 0.7, 0.3}, intensity = 40 }
    },
    layout = {
    { asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
    -- Chairs attached to table base
    { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_2', rot = 180 },
    { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_4', rot = 0 },
        -- Clutter
        { asset_id = 'candles', snap_to = 'dining_table_mega_base.clutter_left', rot = 45 },
        { asset_id = 'candles', snap_to = 'dining_table_mega_base.clutter_right', rot = -30 },
        { asset_id = 'mug', snap_to = 'dining_table_mega_base.clutter_center', rot = 90 }
    }
}
