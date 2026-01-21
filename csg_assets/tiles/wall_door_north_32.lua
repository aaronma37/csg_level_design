return {
    name = "Timber Door Baked V2",
    size = {32, 32},
    metadata = { tile_tags = {"wall", "doorway", "north", "walkable", "v2", "baked"}, nav_mask = 1 },
    layout = { 
        { asset_id = 'wall_door_baked_v2', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'door', pos = {0, 14, 0}, rot = 0 } # Manual offset for door asset
    }
}
