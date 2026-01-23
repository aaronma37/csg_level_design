return {
    name = "Dining Table Mega Scholarly (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega", "cluttered"},
        block_size = {2, 2}
    },
    layout = {
        { id = 'base', asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'chair', snap_to = 'base.seat_1', rot = 180 },
        { asset_id = 'chair', snap_to = 'base.seat_2', rot = 180 },
        { asset_id = 'chair', snap_to = 'base.seat_3', rot = 0 },
        
        { asset_id = 'book_stack', snap_to = 'base.clutter_1', rot = 15 },
        { asset_id = 'book_leaning', snap_to = 'base.clutter_2', rot = 0 },
        { asset_id = 'inkwell', snap_to = 'base.clutter_9', rot = 0 },
        { asset_id = 'scroll', snap_to = 'base.clutter_10', rot = 90 },
        { asset_id = 'candlestick', snap_to = 'base.clutter_center', rot = 0 },
        { asset_id = 'scroll', snap_to = 'base.clutter_3', rot = -15 },
        { asset_id = 'book_vertical', snap_to = 'base.clutter_4', rot = 45 }
    }
}
