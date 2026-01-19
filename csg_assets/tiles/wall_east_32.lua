return {
    name = "Timber Wall East (32x32)",
    size = {32, 32},
    metadata = { 
        tags = {"wall", "indoor", "wood", "east"},
        nav_mask = 0
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Standard East Wall: rot=90, pivot at 26,16
        { asset_id = 'timber_wall_straight_32', pos = {26, 16, 0}, rot = 90 }
    }
}
