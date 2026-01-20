return {
    name = "Timber Wall with Post (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tile_tags = {"wall", "indoor", "wood"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- FLAWLESS: Shares the exact same position as straight walls!
        { asset_id = 'timber_wall_post_32', pos = {16, 26, 0}, rot = 0 }
    }
}
