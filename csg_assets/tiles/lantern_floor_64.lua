return {
    name = "Lantern on Floor (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 1, tags = {"light", "test"} },
    lights = {
        { position = {0, 0, 40}, color = {1.0, 0.8, 0.4}, intensity = 200 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'wall_lantern_64', pos = {0, 0, 40}, rot = 0 }
    }
}
