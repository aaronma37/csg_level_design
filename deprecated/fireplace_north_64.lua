return {
    name = "Fireplace Nook North (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tile_tags = {"wall", "fireplace", "north"} },
    lights = {
        { position = {0, 8, 4}, color = {1.0, 0.6, 0.2}, intensity = 150 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {0, 28, 0}, rot = 0 },
        { asset_id = 'stone_fireplace', pos = {0, 10, 0}, rot = 0 }
    }
}
