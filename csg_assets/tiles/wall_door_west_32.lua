return {
    name = "Timber Doorway West (32x32)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"wall", "doorway", "west", "walkable", "indoor"},
        nav_mask = 1,
        base_height = 0
    },
    layout = {
        { id = 'f', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Rotated 90 degrees to face West (from East orientation)
        { id = 'slot', asset_id = 'timber_wall_door_slot', pos = {-16, 0, 0}, rot = 90 },
        { asset_id = 'door', snap_to = 'slot.door_mount', rot = 0 }
    }
}
