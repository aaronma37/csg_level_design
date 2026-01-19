return {
    name = "Timber Wall Straight (32x32)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"wall", "indoor", "wood"}
    },
    layout = {
        { asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        -- Asset Origin is Center. Thickness 12. Back Face +6.
        -- Target Back Face = 32. So Pivot = 26.
        { asset_id = 'timber_wall_straight_32', pos = {16, 26, 0}, rot = 0 }
    }
}