return {
    name = "Stone Fireplace North Mega (2x1)",
    size = {32, 32},
    metadata = {
        base_height = 0,
        height_type = "flat",
        nav_mask = 0,
        tags = {"furniture", "fireplace", "mega", "north"},
        block_size = {2, 1}
    },
    layout = {
        { id = 'f1', asset_id = 'floor_bevel_32', pos = {0, 0, 0}, rot = 0 },
        { id = 'f2', asset_id = 'floor_bevel_32', pos = {32, 0, 0}, rot = 0 },
        
        -- Walls (Snap to Floor North)
        { id = 'w1', asset_id = 'timber_wall_32', snap_to = 'f1.north', snap_from = 'front', rot = 180 },
        { id = 'w2', asset_id = 'timber_wall_32', snap_to = 'f2.north', snap_from = 'front', rot = 180 },
        
        -- Fireplace
        -- Snap Back to Wall Front?
        -- w1 Front is at f1.north.
        -- Snap Fireplace Back to f1.north?
        -- But Fireplace needs to be centered between tiles (X=16 relative to f1).
        -- If we have a 'center' snap on floor?
        -- f1.center is `0,0`.
        -- We want X=16.
        -- We can snap to `f1.north` and then offset manually?
        -- Or define a virtual anchor?
        -- Or just rely on `stone_fireplace` snap `back`.
        -- And place it relative to...
        -- If I place it at `pos={16, -16}`.
        -- Snap to? No, manual pos is fallback.
        -- Can I use `snap_to` with an offset? No (simple compiler).
        -- I'll stick to manual pos for Fireplace for now, or assume I can snap to `w1.right`?
        -- w1.right is `[16, 6]`. (Local).
        -- Rot 180 -> `[-16, -6]`.
        -- Global: `Pos[0, -16] + [-16, -6] = [-16, -22]`.
        -- X is -16.
        -- I want X = 16.
        -- `w1` is at 0. `w2` is at 32.
        -- `w1.right` is at 16? No.
        -- `timber_wall_32` X `[-16, 16]`.
        -- Right is 16.
        -- Rot 180 -> -16.
        -- Pos X=0. Result -16.
        -- Wait. Rot 180 flips X.
        -- So Right (16) becomes Left (-16).
        -- Left (-16) becomes Right (16).
        -- So I should snap to `w1.left` (which becomes Global Right).
        -- `w1.left` -> 16.
        -- `w1` Pos X=0.
        -- Global X = 16.
        -- Perfect.
        -- Y? Wall `left` is at Y=6 (Center).
        -- Global Y = `Pos(-16) + Rot(-6) = -22`.
        -- Fireplace `back` is Y=3.
        -- If I snap `back` to `w1.left`.
        -- Target Y = -22.
        -- Fireplace Rot 180 -> Back = -3.
        -- `Pos + (-3) = -22` -> `Pos = -19`.
        -- I want Back at -16 (Flush with Wall Front).
        -- So `w1.left` Y is too deep (Center).
        -- I need `w1.front_right`? (Front Face, Right Edge).
        -- I didn't define that.
        -- I'll stick to manual for Fireplace to avoid complexity.
        { asset_id = 'stone_fireplace', pos = {16, -13, 0}, rot = 180 }
    }
}