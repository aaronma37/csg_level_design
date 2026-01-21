import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import palette
from patterns import csg_patterns

def generate_slotted_walls():
    # Base dimensions for a 64-unit wall segment
    w_len, w_h, mid_z = 64, 140, 46
    beam_thick, beam_h_dim = 12, 6
    plaster_thick = 4
    back_y = beam_thick - plaster_thick

    def make_base_instructions():
        inst = []
        # Beams only (No plaster yet)
        for z in [0, mid_z, w_h - beam_h_dim]:
            inst.append({"op": "add", "pos": [0, 0, z], "size": [w_len, beam_thick, beam_h_dim], "color": palette.WOOD_DARK})
        for x in [0, w_len - 6]:
            inst.append({"op": "add", "pos": [x, 0, 0], "size": [6, beam_thick, w_h], "color": palette.WOOD_DARK})
        return inst

    # 1. WINDOW SLOT (Centered)
    win_inst = make_base_instructions()
    # Add plaster but leave a hole 24x32 at Z=68
    for x in range(0, w_len, 4):
        for z in range(0, w_h, 4):
            # Hole logic
            if x >= 20 and x < 44 and z >= 68 and z < 100: continue
            
            color = palette.BEIGE_LIGHT if z > mid_z else palette.STONE_LIGHT
            win_inst.append({"op": "add", "pos": [x, back_y, z], "size": [4, plaster_thick, 4], "color": color})
    
    with open("csg/timber_wall_window_slot.json", "w") as f:
        json.dump({"name": "timber_wall_window_slot", "instructions": win_inst}, f, indent=2)

    # 2. DOOR SLOT (Centered)
    door_inst = make_base_instructions()
    # Hole 30x50 at Z=0
    for x in range(0, w_len, 4):
        for z in range(0, w_h, 4):
            if x >= 17 and x < 47 and z < 50: continue
            color = palette.BEIGE_LIGHT if z > mid_z else palette.STONE_LIGHT
            door_inst.append({"op": "add", "pos": [x, back_y, z], "size": [4, plaster_thick, 4], "color": color})

    with open("csg/timber_wall_door_slot.json", "w") as f:
        json.dump({"name": "timber_wall_door_slot", "instructions": door_inst}, f, indent=2)

if __name__ == "__main__":
    generate_slotted_walls()
