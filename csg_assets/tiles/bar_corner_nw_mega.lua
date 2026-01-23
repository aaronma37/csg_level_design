return {
    name = "Bar Corner Mega (2x2)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"furniture", "bar", "mega"},
        block_size = {2, 2}
    },
    layout = {
        -- Use the integrated base asset at origin
        { id = 'base', asset_id = 'bar_corner_mega_base', pos = {0, 0, 0}, rot = 0 },
        
        -- Clutter (Using snap points)
        { asset_id = 'candles', snap_to = 'base.candle_spot', rot = 0 }, 
        { asset_id = 'mug', snap_to = 'base.mug_spot', rot = 45 }
    }
}
