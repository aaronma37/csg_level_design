return {
    name = "Dining Table Mega Var1 (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 2}
    },
    layout = {
            { asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
            -- Chairs attached to table base
            { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_1', rot = 180 },
            { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_3', rot = 0 },        -- Clutter (Using new surface snap points)
        { asset_id = 'candles', snap_to = 'dining_table_mega_base.clutter_center', rot = 0 },
        { asset_id = 'mug', snap_to = 'dining_table_mega_base.clutter_left', rot = 20 },
        { asset_id = 'mug', snap_to = 'dining_table_mega_base.clutter_right', rot = -45 }
    }
}
