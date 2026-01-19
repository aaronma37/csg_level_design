return {
    name = "Timber Wall with Post (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- JSON normalized: Origin is middle of wall part.
        -- Aligning middle of wall to same line as straight walls.
        { asset_id = 'timber_wall_post_32', pos = {16, 26, 0}, rot = 0 }
    }
}