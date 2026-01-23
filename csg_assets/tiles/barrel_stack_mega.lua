return {
    name = "Barrel Stack Mega (2x1)",
    size = {32, 32},
    metadata = { 
        tile_tags = {"prop", "barrel", "mega", "storage"},
        block_size = {2, 1}
    },
    layout = {
        { id = 'base', asset_id = 'barrel_stack_mega_base', pos = {0, 0, 0}, rot = 0 },
        
        { asset_id = 'barrel_side', snap_to = 'base.b_1_1', rot = -2 },
        { asset_id = 'barrel_side', snap_to = 'base.b_1_2', rot = 3 },
        { asset_id = 'barrel_side', snap_to = 'base.b_1_3', rot = -1 },
        
        { asset_id = 'barrel_side', snap_to = 'base.b_2_1', rot = 5 },
        { asset_id = 'barrel_side', snap_to = 'base.b_2_2', rot = -4 },
        
        { asset_id = 'barrel_side', snap_to = 'base.b_3_1', rot = 0 }
    }
}