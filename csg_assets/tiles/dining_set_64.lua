return {
    name = "Dining Set (64x64)",
    size = {64, 64},
    metadata = { base_height = 0, nav_mask = 0, tags = {"furniture", "table"} },
    layout = {
        { asset_id = 'floor_64', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'medieval_feast_table', pos = {0, 0, 0}, rot = 0 },
        -- Chairs facing the table
        { asset_id = 'chair', pos = {0, 20, 0}, rot = 0 },
        { asset_id = 'chair', pos = {0, -20, 0}, rot = 180 }
    }
}
