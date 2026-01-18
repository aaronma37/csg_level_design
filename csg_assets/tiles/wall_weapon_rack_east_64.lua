return {
    name = "East Wall Weapon Rack (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "east", "weapons"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {28, 0, 0}, rot = 90 },
        -- Rack on East wall (X edge). Rotate 90.
        { asset_id = 'weapon_rack', pos = {19, 0, 0}, rot = 90 }
    }
}
