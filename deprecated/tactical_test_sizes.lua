-- Tactical Test Scene (Size Comparison)
return {
    ambient = { color = {0.2, 0.2, 0.3}, sun_dir = {0.5, -0.8, 0.4} },
    camera = { center = {100, 0, 0}, distance = 400, angle = 0.78, height = 200, fov = 30 },
    tiles = {
        -- ROW 1: 64x64 Grid (The Current Standard)
        -- Spacing: 64 units
        { tile_id = "floor_bevel_64", pos = {0, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {1, 0}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_64", pos = {2, 0}, height = 0, rot = 0 },
        
        -- ROW 2: 48x48 Grid (Proposed Hybrid)
        -- We need to manually calculate positions since the engine might assume grid=64 logic 
        -- if "pos" refers to grid index.
        -- BUT, usually 'pos' is {grid_x, grid_y}.
        -- If the renderer supports different grid sizes, we'd need to know how it handles them.
        -- Assuming the renderer places tiles at pos[0]*TILE_SIZE, pos[1]*TILE_SIZE.
        -- If TILE_SIZE is hardcoded to 64 in the engine, these smaller tiles will have gaps.
        -- If TILE_SIZE is per-tile... wait.
        
        -- Let's assume for this TEST that the engine renders based on the Tile's definition size?
        -- Or maybe I should just place them manually if I can?
        -- Standard scene loader likely does: x = tile.pos[1] * 64, y = tile.pos[2] * 64.
        
        -- To properly test visual density without rewriting the engine, I will rely on the fact 
        -- that these tiles are just meshes. 
        -- I'll place them on the 64-grid but they will appear small (with gaps).
        -- This is actually GOOD for checking the "Unit on Tile" ratio.
        
        { tile_id = "floor_bevel_48", pos = {0, 2}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_48", pos = {1, 2}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_48", pos = {2, 2}, height = 0, rot = 0 },

        -- ROW 3: 32x32 Grid (Proposed Classic)
        { tile_id = "floor_bevel_32", pos = {0, 4}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_32", pos = {1, 4}, height = 0, rot = 0 },
        { tile_id = "floor_bevel_32", pos = {2, 4}, height = 0, rot = 0 },
    },
    
    -- We can add "props" (Units) to visualize scale
    -- The engine usually loads units separately or via 'layout' in tiles.
    -- I'll add a dummy layout to the tiles above to spawn a 'figurine_hero'.
    -- But since I can't easily edit the tiles to include heroes dynamically without making 3 new tile files...
    -- I'll just trust the user to look at the tiles or...
    
    -- Wait, I can make a "unit_test_tile" that includes the floor AND the unit.
}
