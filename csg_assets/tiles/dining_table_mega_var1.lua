return {
    name = "Dining Table Mega Var1 (2x1)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "table", "mega"},
        block_size = {2, 1}
    },
    lights = {
        -- Light for the central candle
        { position = {32, 25, 32}, color = {1.0, 0.8, 0.4}, intensity = 50 }
    },
    layout = {
        -- Table Center: 32, 16
        { asset_id = 'medieval_feast_table', pos = {32, 16, 0}, rot = 0 },
        
        -- Chairs
        { asset_id = 'chair', pos = {32, 36, 0}, rot = 0 },
        { asset_id = 'chair', pos = {32, -4, 0}, rot = 180 },
        
        -- Clutter
        -- Candle Center
        { asset_id = 'candles', pos = {32, 16, 26}, rot = 0 },
        -- Mugs
        { asset_id = 'mug', pos = {24, 10, 26}, rot = 20 },
        { asset_id = 'mug', pos = {40, 22, 26}, rot = -45 }
    }
}
