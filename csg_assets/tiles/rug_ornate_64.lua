return {
    name = "Ornate Rug (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 1, tile_tags = {"clutter", "rug", "walkable"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        -- Rug sitting on floor (Z=1 to sit on planks)
        { asset_id = 'ornate_rug', pos = {0, 0, 2}, rot = 0 }
    }
}
