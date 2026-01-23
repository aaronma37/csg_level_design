return {
    name = "Single Barrel Tile",
    size = {32, 32},
    metadata = { 
        tile_tags = {"prop", "barrel", "storage", "floor"},
        nav_mask = 1
    },
    layout = {
        { id = 'base', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { asset_id = 'barrel', pos = {16, 16, 0}, rot = 0 } -- Center of tile (0..32) is 16,16? 
        -- If asset is centered at 0,0, then putting it at 16,16 places it in the center of the tile.
    }
}