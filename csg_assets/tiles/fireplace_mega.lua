return {
    name = "Stone Fireplace Mega (2x1)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"furniture", "fireplace", "mega"},
        block_size = {2, 1}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'floor_bevel_32', pos = {32, 0, 0}, rot = 0 },
        -- North Walls
        { asset_id = 'timber_wall_straight_32', pos = {16, 26, 0}, rot = 0 },
        { asset_id = 'timber_wall_straight_32', pos = {48, 26, 0}, rot = 0 },
        -- Fireplace (Pivot 18 to align back with wall back)
        { asset_id = 'stone_fireplace', pos = {32, 18, 0}, rot = 0 }
    }
}