return {
    name = "Bar Corner Mega (2x2)",
    size = {32, 32}, -- Fixed grid size
    metadata = { 
        tile_tags = {"furniture", "bar", "mega"},
        block_size = {2, 2}
    },
    lights = {
        -- Shift light by +16, +16
        { position = {32, 44, 45}, color = {1.0, 0.7, 0.3}, intensity = 100 }
    },
    layout = {
        -- Centered on 2x2 block (32, 32 relative to anchor corner)
        { asset_id = 'bar_corner_64', pos = {32, 32, 0}, rot = 0 },
        
        -- Candles and Mugs (Shifted +16 from original 16 -> +32 relative to 0?) 
        -- Original: -8 (relative to 16?). No, pos in layout is absolute.
        -- Previous: 16 (Center). Item at -8. Relative = -24.
        -- New Center: 32. Item at 32 - 24 = 8?
        -- Wait, Previous 'pos' was the transform of the object.
        -- Asset Origin 0. Placed at 16.
        -- Item 'candles' placed at -8.
        -- This implies 'candles' is NOT attached to the bar, but separate item in the list.
        -- So 'candles' pos is in Tile Coordinates.
        -- Previous: -8.
        -- If Origin was Center (16). -8 is 24 units Left of Center.
        -- New Origin Corner (0). Center 32.
        -- 24 units Left of 32 = 8.
        -- So -8 -> 8. (Shift +16).
        
        -- Check Mugs:
        -- Previous: 6. (10 units Left of 16).
        -- New: 32 - 10 = 22.
        -- Shift +16.
        
        { asset_id = 'candles', pos = {8, 56, 38}, rot = 0 }, -- -8 + 16 = 8. Y: 40 + 16 = 56.
        { asset_id = 'mug', pos = {22, 56, 38}, rot = 45 }      -- 6 + 16 = 22. Y: 40 + 16 = 56.
    }
}