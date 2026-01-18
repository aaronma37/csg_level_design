return {
    name = "Tavern Wall East (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"wall", "east"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        -- East edge is x=28, wall rotated 90
        { asset_id = 'tavern_wall_tall', pos = {28, 0, 0}, rot = 90 }
    }
}
