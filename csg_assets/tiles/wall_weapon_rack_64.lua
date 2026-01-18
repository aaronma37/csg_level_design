return {
    name = "Wall Weapon Rack (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "north", "weapons"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {0, 28, 0}, rot = 0 },
        -- Weapon rack in front of wall. 
        -- Wall is at y=28. Rack is 10 deep. 24 - 5 = 19.
        { asset_id = 'weapon_rack', pos = {0, 19, 0}, rot = 0 }
    }
}
