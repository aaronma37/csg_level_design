return {
    name = "Timber Wall NE Corner (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood", "corner"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- North Side
        { asset_id = 'timber_wall_straight_32', pos = {16, 26, 0}, rot = 0 },
        -- East Side
        { asset_id = 'timber_wall_straight_32', pos = {26, 16, 0}, rot = 90 },
        -- Corner Pillar
        { asset_id = 'stone_pillar', pos = {26, 26, 0}, rot = 0 }
    }
}