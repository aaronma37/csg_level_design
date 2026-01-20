return {
    name = "Wooden Stairs (80x80)",
    size = {80, 80},
    metadata = {
        base_height = 0,
        height_type = "slope",
        slope_dir = "north", -- Rising towards north (+Y)
        nav_mask = 1,
        tile_tags = {"wood", "stairs", "walkable"}
    },
    layout = {
        { asset_id = 'stairs', pos = {-40, -40, 0}, rot = 0 }
    }
}
