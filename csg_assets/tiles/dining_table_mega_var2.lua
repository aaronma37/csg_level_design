return {
    name = "Dining Table Mega Var2 (2x1)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 1}
    },
    lights = {
        -- Lights for two candles
        { position = {20, 25, 32}, color = {1.0, 0.7, 0.3}, intensity = 40 },
        { position = {44, 25, 32}, color = {1.0, 0.7, 0.3}, intensity = 40 }
    },
    layout = {
        -- Table Center: 32, 16
        { asset_id = 'medieval_feast_table', pos = {32, 16, 0}, rot = 0 },
        
        -- Chairs (Added side chairs for variety?)
        { asset_id = 'chair', pos = {32, 36, 0}, rot = 0 },
        { asset_id = 'chair', pos = {32, -4, 0}, rot = 180 },
        
        -- Clutter
        -- Candles
        { asset_id = 'candles', pos = {20, 16, 26}, rot = 45 },
        { asset_id = 'candles', pos = {44, 16, 26}, rot = -30 },
        -- Mugs
        { asset_id = 'mug', pos = {32, 10, 26}, rot = 90 },
        { asset_id = 'mug', pos = {32, 22, 26}, rot = -90 }
    }
}
