return {
    name = "Dining Table Mega (2x1)",
    size = {32, 32},
    metadata = { 
        tags = {"furniture", "table", "mega"},
        block_size = {2, 1}
    },
    layout = {
        -- Asset normalized (Center 0,0).
        -- 2x1 Block Center: {32, 16, 0} relative to Anchor Corner.
        { asset_id = 'medieval_feast_table', pos = {32, 16, 0}, rot = 0 },
        
        -- Chairs
        -- Top Chair: 0, 20 relative to table center?
        -- Table Center is 32, 16.
        -- Top Chair: 32, 16+20 = 36.
        { asset_id = 'chair', pos = {32, 36, 0}, rot = 0 },
        -- Bottom Chair: 32, 16-20 = -4.
        { asset_id = 'chair', pos = {32, -4, 0}, rot = 180 }
    }
}