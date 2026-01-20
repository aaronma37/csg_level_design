return {
    name = "Timber Wall NW Corner (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood", "corner"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- North Wall Segment
        { asset_id = 'timber_wall_32', pos = {0, -8, 0}, rot = 180 },
        -- West Wall Segment (Rot 270)
        -- X Pos = -8.
        { asset_id = 'timber_wall_32', pos = {-8, 0, 0}, rot = 270 },
        -- Corner Pillar
        -- Centered on junction (-8, -8)
        { asset_id = 'stone_pillar', pos = {-8, -8, 0}, rot = 0 }
    }
}