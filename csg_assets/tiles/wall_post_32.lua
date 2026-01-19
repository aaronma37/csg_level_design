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
        -- Crossbeam Correction:
        -- Straight Center: 6. New Center: -10. Difference: 16.
        -- Shift: +16 (Backwards). Compensation: -16 (Forward).
        -- 20 - 16 = 4.
        { asset_id = 'timber_wall_post_32', pos = {0, 4, 0}, rot = 0 }
    }
}