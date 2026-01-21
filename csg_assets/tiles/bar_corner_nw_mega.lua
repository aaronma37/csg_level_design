return {
    name = "Bar Corner Mega (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "bar", "mega"},
        block_size = {2, 2}
    },
    lights = {
        { position = {32, 44, 45}, color = {1.0, 0.7, 0.3}, intensity = 100 }
    },
    layout = {
        -- Use the integrated base asset at origin
        { asset_id = 'bar_corner_mega_base', pos = {0, 0, 0}, rot = 0 },
        
        -- Clutter (Adjusted to new coordinate system if needed, but 0,0 is the same reference)
        -- Previous logic used pos={32,32} for the bar. 
        -- If I change bar to 0,0, I need to shift clutter by -32, -32?
        -- Let's check:
        -- Original candles: {8, 56, 38} (Relative to 0,0)
        -- If Bar was at 32,32 and candles at 8,56... candles were behind/left of bar.
        -- Let's stick to the relative positions.
        { asset_id = 'candles', pos = {8, 56, 38}, rot = 0 }, 
        { asset_id = 'mug', pos = {22, 56, 38}, rot = 45 }
    }
}
