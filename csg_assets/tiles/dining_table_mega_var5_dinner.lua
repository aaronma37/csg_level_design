return {
    name = "Dining Table Mega Dinner (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega", "dinner"},
        block_size = {2, 2}
    },
    layout = {
        { id = 'base', asset_id = 'dining_table_mega_base', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'chair', snap_to = 'base.seat_1', rot = 180 },
        { asset_id = 'chair', snap_to = 'base.seat_2', rot = 180 },
        { asset_id = 'chair', snap_to = 'base.seat_3', rot = 0 },
        { asset_id = 'chair', snap_to = 'base.seat_4', rot = 0 },
        
        -- Place settings
        { asset_id = 'plate', snap_to = 'base.clutter_1', rot = 0 },
        { asset_id = 'fork', snap_to = 'base.clutter_1', rot = 0, pos = {-6, 0, 0} },
        { asset_id = 'knife', snap_to = 'base.clutter_1', rot = 0, pos = {6, 0, 0} },
        { asset_id = 'mug', snap_to = 'base.clutter_1', rot = 0, pos = {10, 8, 0} },

        { asset_id = 'plate', snap_to = 'base.clutter_4', rot = 0 },
        { asset_id = 'fork', snap_to = 'base.clutter_4', rot = 0, pos = {-6, 0, 0} },
        { asset_id = 'knife', snap_to = 'base.clutter_4', rot = 0, pos = {6, 0, 0} },
        { asset_id = 'mug', snap_to = 'base.clutter_4', rot = 0, pos = {-10, 8, 0} },

        { asset_id = 'plate', snap_to = 'base.clutter_5', rot = 0 },
        { asset_id = 'fork', snap_to = 'base.clutter_5', rot = 0, pos = {-6, 0, 0} },
        { asset_id = 'knife', snap_to = 'base.clutter_5', rot = 0, pos = {6, 0, 0} },
        { asset_id = 'mug', snap_to = 'base.clutter_5', rot = 0, pos = {10, -8, 0} },

        { asset_id = 'plate', snap_to = 'base.clutter_8', rot = 0 },
        { asset_id = 'fork', snap_to = 'base.clutter_8', rot = 0, pos = {-6, 0, 0} },
        { asset_id = 'knife', snap_to = 'base.clutter_8', rot = 0, pos = {6, 0, 0} },
        { asset_id = 'mug', snap_to = 'base.clutter_8', rot = 0, pos = {-10, -8, 0} },

        -- Central Clutter
        { asset_id = 'candlestick', snap_to = 'base.clutter_center', rot = 0 },
        { asset_id = 'book_stack', snap_to = 'base.clutter_10', rot = 15 },
        { asset_id = 'scroll', snap_to = 'base.clutter_12', rot = -45 }
    }
}