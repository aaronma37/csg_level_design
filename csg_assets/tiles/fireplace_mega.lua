return {
    name = "Stone Fireplace Mega (2x1)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tile_tags = {"furniture", "fireplace", "mega"},
        block_size = {2, 2}
    },
    layout = {
        -- Base Asset containing Floor + Fireplace + Back Walls
        -- Note: Asset Origin (0,0,0) corresponds to Tile Anchor (Top-Left of first cell).
        { asset_id = 'fireplace_mega_base', pos = {0, 0, 0}, rot = 0 },
        
        -- Props attached to Snap Points defined in the Base Asset
        { asset_id = 'ornate_rug', snap_to = 'fireplace_mega_base.hearth_rug', rot = 0 },
        { asset_id = 'chair', snap_to = 'fireplace_mega_base.chair_left', rot = -45 }, -- Angled inward
        { asset_id = 'chair', snap_to = 'fireplace_mega_base.chair_right', rot = 45 }, -- Angled inward
        { asset_id = 'candles', snap_to = 'fireplace_mega_base.mantle_left', rot = 0 },
        { asset_id = 'skull', snap_to = 'fireplace_mega_base.mantle_right', rot = 15 }
    }
}