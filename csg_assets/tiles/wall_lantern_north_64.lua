return {
    name = "Wall Lantern North (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "north", "light"} },
    lights = {
        { position = {0, 10, 90}, color = {1.0, 0.7, 0.3}, intensity = 250 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_tall', pos = {0, 28, 0}, rot = 0 },
        -- Front of wall is y=24. The lantern origin is now grounded/centered by vox_to_gltf.
        -- So pos y=24 will put the wall plate exactly on the surface.
        { asset_id = 'wall_lantern_64', pos = {0, 24, 90}, rot = 0 }
    }
}
