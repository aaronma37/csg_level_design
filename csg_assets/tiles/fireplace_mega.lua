return {
    name = "Stone Fireplace Mega (2x1)",
    size = {32, 32}, -- Fixed grid size to 32
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0, -- Obstacle
        tags = {"furniture", "fireplace", "mega"},
        block_size = {2, 1}
    },
    layout = {
        -- Position {32, 2, 0}: Centered on 2-tile block (X=32), Touching North Wall (Y=2 + 14 = 16)
        -- Rotation 0: Face South (Out of the wall, assuming model Back is Y+)
        { asset_id = 'stone_fireplace', pos = {32, 2, 0}, rot = 0 }
    }
}