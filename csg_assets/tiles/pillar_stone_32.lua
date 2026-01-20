return {
    name = "Stone Pillar Tile (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tile_tags = {"stone", "obstacle"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'stone_pillar', pos = {0, 0, 0}, rot = 0 }
    }
}
