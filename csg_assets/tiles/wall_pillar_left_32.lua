return {
    name = "Timber Wall Pillar Left (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood", "pillar"}
    },
    layout = {
        -- Fixed asset_id from floor_wood_32 to floor_bevel_32
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Standardized North Wall Position
        { asset_id = 'timber_wall_pillar_left_32', pos = {16, 26, 0}, rot = 0 }
    }
}
