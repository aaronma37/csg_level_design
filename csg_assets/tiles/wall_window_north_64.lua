return {
    name = "Tavern Wall North Window (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "north", "window"} },
    lights = {
        -- Cool moonlight coming through the window
        { position = {0, 20, 100}, color = {0.4, 0.6, 1.0}, intensity = 100 }
    },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'tavern_wall_window', pos = {0, 28, 0}, rot = 0 },
        -- Insert the window into the wall cutout
        { asset_id = 'window_64', pos = {0, 28, 70}, rot = 0 }
    }
}
