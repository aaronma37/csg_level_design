return {
    name = "Bar Straight Mega (2x2)",
    size = {32, 32}, -- Fixed grid size
    metadata = { 
        tile_tags = {"furniture", "bar", "mega"},
        block_size = {2, 2}
    },
    layout = {
        -- Asset normalized (Center 0,0). Y shift was -8.
        -- Previous pos {32, 52}. Add 8 to compensate -> {32, 60}.
        { asset_id = 'bar_straight_64', pos = {32, 60, 0}, rot = 0 },
        
        -- Mugs (Shifted with bar? Mugs were absolute pos).
        -- If Bar moved, Mugs should move if they were relative?
        -- But layout pos is absolute in tile.
        -- Mugs were visually aligned to the OLD bar.
        -- If Bar moved visually (by me shifting pos to compensate asset shift), the Bar Visual stays in same place.
        -- So Mugs should stay in same place.
        -- Previous Mugs: {17, 57}, {42, 54}.
        -- I'll keep them there.
        { asset_id = 'mug', pos = {17, 57, 38}, rot = 15 },
        { asset_id = 'mug', pos = {42, 54, 38}, rot = 110 }
    }
}
