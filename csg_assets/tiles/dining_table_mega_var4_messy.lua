return {
    name = "Dining Table Mega Messy (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega", "messy"},
        block_size = {2, 2}
    },
    layout = {
        { id = 'base', asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'chair', snap_to = 'base.seat_1', rot = 160 },
        { asset_id = 'chair', snap_to = 'base.seat_4', rot = -20 },
        
        { asset_id = 'mug', snap_to = 'base.clutter_5', rot = 0 },
        { asset_id = 'mug', snap_to = 'base.clutter_left', rot = 45 },
        { asset_id = 'scroll', snap_to = 'base.clutter_6', rot = 110 },
        { asset_id = 'candlestick', snap_to = 'base.clutter_12', rot = 0 },
        { asset_id = 'mug', snap_to = 'base.clutter_7', rot = -10 },
        { asset_id = 'book_stack', snap_to = 'base.clutter_8', rot = 190 }
    }
}
