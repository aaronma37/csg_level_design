return {
    name = "Stone Fireplace Mega (2x1)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0, -- Obstacle
        tags = {"furniture", "fireplace", "mega"},
        block_size = {2, 1}
    },
    layout = {
        -- Walls (Background)
        { asset_id = 'timber_wall_straight_32', pos = {0, 20, 0}, rot = 0 },
        { asset_id = 'timber_wall_straight_32', pos = {32, 20, 0}, rot = 0 },

        -- Fireplace (Embedded)
        -- Position {32, 18, 0}: Center X=32. Y=18 -> Back Face at 18+14=32 (Flush with Wall Back).
        -- Rotation 0: Face South.
        { asset_id = 'stone_fireplace', pos = {32, 18, 0}, rot = 0 }
    }
}
