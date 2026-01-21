-- Tactical Test Scene (6x6 Expanded)
return {
    ambient = { color = {0.2, 0.2, 0.3}, sun_dir = {0.5, -0.8, 0.4} },
    camera = { center = {160, 0, 160}, distance = 600, angle = 0.78, height = 300, fov = 30 },
    tiles = {
        -- Row 0 (South)
        { tile_id = "floor_bevel_64", pos = {0, 0}, height = 0, rot = 0 },
        { tile_id = "rug_ornate_64", pos = {1, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {2, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {3, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {4, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {5, 0}, height = 0, rot = 0 },
        
        -- Row 1 (Bar Area)
        { tile_id = "bar_corner_nw_64", pos = {0, 1}, height = 0, rot = 0 },
        { tile_id = "bar_north_64",     pos = {1, 1}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {2, 1}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {3, 1}, height = 0, rot = 0 },
        { tile_id = "dining_clutter_64", pos = {4, 1}, height = 0, rot = 0 },
        { tile_id = "wall_east_64",     pos = {5, 1}, height = 0, rot = 0 },

        -- Row 2 (Mid Room)
        { tile_id = "barrel_clutter_64", pos = {0, 2}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {1, 2}, height = 0, rot = 0 },
        { tile_id = "dining_clutter_64", pos = {2, 2}, height = 0, rot = 0 },
        { tile_id = "dining_clutter_64", pos = {3, 2}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {4, 2}, height = 0, rot = 0 },
        { tile_id = "wall_east_64",     pos = {5, 2}, height = 0, rot = 0 },

        -- Row 3 (Stairs Area)
        { tile_id = "floor_bevel_64",    pos = {0, 3}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {1, 3}, height = 0, rot = 0 },
        { tile_id = "stairs_north_64",  pos = {2, 3}, height = 0, rot = 0 },
        { tile_id = "stairs_north_64",  pos = {3, 3}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {4, 3}, height = 0, rot = 0 },
        { tile_id = "wall_weapon_rack_east_64", pos = {5, 3}, height = 0, rot = 0 },

        -- Row 4 (Elevated Platform)
        { tile_id = "floor_bevel_64",    pos = {0, 4}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {1, 4}, height = 0, rot = 0 },
        { tile_id = "block_wood_64",    pos = {2, 4}, height = 0, rot = 0 },
        { tile_id = "block_wood_64",    pos = {3, 4}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64",    pos = {4, 4}, height = 0, rot = 0 },
        { tile_id = "wall_east_64",     pos = {5, 4}, height = 0, rot = 0 },

        -- Row 5 (North Wall)
        { tile_id = "wall_window_north_64",  pos = {0, 5}, height = 0, rot = 0 },
        { tile_id = "fireplace_north_64",    pos = {1, 5}, height = 0, rot = 0 },
        { tile_id = "wall_lantern_north_64", pos = {2, 5}, height = 16, rot = 0 }, -- On block
        { tile_id = "wall_lantern_north_64", pos = {3, 5}, height = 16, rot = 0 }, -- On block
        { tile_id = "wall_bookshelf_north_64", pos = {4, 5}, height = 0, rot = 0 },
        { tile_id = "wall_corner_64",        pos = {5, 5}, height = 0, rot = 0 },
    }
}
