return {
    name = "Timber Doorway North V2 (32x32)",
    size = {32, 32},
    metadata = { tile_tags = {"wall", "doorway", "north", "walkable", "indoor", "v2"}, nav_mask = 1 },
    layout = {
        { id = 'f', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { id = 'slot', asset_id = 'door_slot_v2', snap_to = 'f.north', snap_from = 'front', rot = 180 },
        { asset_id = 'door', snap_to = 'slot.door_mount', rot = 0 }
    }
}
