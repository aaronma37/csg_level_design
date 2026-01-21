return {
    name = "Dining Table Mega (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 2}
    },
    layout = {
        { asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
        -- Chairs attached to table base
        { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_1', rot = 0 },
        { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_2', rot = 0 },
        { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_3', rot = 180 },
        { asset_id = 'chair', snap_to = 'dining_table_mega_base.seat_4', rot = 180 }
    }
}
