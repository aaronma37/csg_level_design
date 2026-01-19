return {
    name = "Timber Wall NW Corner (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood", "corner"}
    },
    layout = {
        -- North Side
        { asset_id = 'timber_wall_straight_32', pos = {0, 20, 0}, rot = 0 },
        -- West Side
        { asset_id = 'timber_wall_straight_32', pos = {12, 0, 0}, rot = 90 },
        -- Corner Pillar (To hide the seam)
        { asset_id = 'stone_pillar', pos = {6, 26, 0}, rot = 0 }
    }
}
