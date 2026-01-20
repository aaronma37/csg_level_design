return {
    name = "Dining Table Mega (2x1)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 1}
    },
    layout = {
        -- Base Floor (Anchor Cell)
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },

        -- Asset normalized (Center 0,0).
        -- 2x1 Block Center: {32, 16, 0} relative to Anchor Corner.
        { asset_id = 'medieval_feast_table', pos = {32, 16, 0}, rot = 0 },
        
        -- Chairs
        { asset_id = 'chair', pos = {32, 36, 0}, rot = 0 },
        { asset_id = 'chair', pos = {32, -4, 0}, rot = 180 },
        
        -- Clutter
        -- Bottle in center
        { asset_id = 'bottle', pos = {32, 16, 26}, rot = 0 },
        
        -- Tankards
        { asset_id = 'tankard', pos = {24, 12, 26}, rot = 30 },
        { asset_id = 'tankard', pos = {40, 20, 26}, rot = -120 }
    }
}
