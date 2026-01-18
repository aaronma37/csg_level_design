return {
    name = "Wall Barrels North (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "north", "barrels"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {0, 28, 0}, rot = 0 },
        -- Barrels against the wall
        { asset_id = 'barrel', pos = {-15, 12, 0}, rot = 0 },
        { asset_id = 'barrel', pos = {15, 12, 0}, rot = 0 }
    }
}
