return {
    name = "Bookshelf Mega (2x1)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "bookshelf", "mega", "storage"},
        block_size = {2, 1}
    },
    layout = {
        { id = 'base', asset_id = 'bookshelf_mega_base', pos = {0, 0, 0}, rot = 0 },
        
        -- Candles on top
        { asset_id = 'candles', snap_to = 'base.top_left', rot = 0 },
        { asset_id = 'candles', snap_to = 'base.top_right', rot = 30 },
        
        -- Bottom Shelf (Shelf 1)
        { asset_id = 'book_vertical', snap_to = 'base.s1_l_1', rot = 5 },
        { asset_id = 'book_vertical', snap_to = 'base.s1_l_2', rot = -5 },
        { asset_id = 'book_stack',    snap_to = 'base.s1_l_3', rot = 10 },
        
        { asset_id = 'book_leaning',  snap_to = 'base.s1_r_1', rot = 0 },
        { asset_id = 'book_vertical', snap_to = 'base.s1_r_2', rot = 0 },

        -- Middle Shelf (Shelf 2)
        { asset_id = 'book_stack',    snap_to = 'base.s2_l_1', rot = -10 },
        { asset_id = 'book_vertical', snap_to = 'base.s2_r_1', rot = 0 },
        { asset_id = 'book_leaning',  snap_to = 'base.s2_r_2', rot = 180 },

        -- Top Shelf (Shelf 3)
        { asset_id = 'book_vertical', snap_to = 'base.s3_l_1', rot = 15 },
        { asset_id = 'book_stack',    snap_to = 'base.s3_r_1', rot = 0 }
    }
}