return {
    name = "Timber Wall East Post (32x32)",
    size = {32, 32},
    metadata = { 
        tags = {"wall", "indoor", "wood", "east", "post"},
        nav_mask = 0
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Beefy Post at East side: uses the SAME logic as North but rotated
        { asset_id = 'timber_wall_post_32', pos = {26, 16, 0}, rot = 90 }
    }
}
