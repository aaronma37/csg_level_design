import json
import os
import random

def create_layout():
    random.seed(42) # Deterministic chaos
    layout = []

    # --- Structural ---
    # 2x2 Floor (320x320)
    for x in [0, 160]:
        for y in [0, 160]:
            layout.append({"asset_id": "wooden_floor", "pos": [x, y, -2], "rot": 0})

    # North Wall (Covering 320 units)
    for x in [0, 64, 128, 192, 256]:
        layout.append({"asset_id": "timber_wall", "pos": [x, 308, 0], "rot": 0})
    
    # East Wall (Covering 320 units)
    for y in [0, 64, 128, 192, 256]:
        layout.append({"asset_id": "timber_wall", "pos": [308, y, 0], "rot": 90})

    # Mezzanine Walkway (North and East)
    layout.append({"asset_id": "walkway_tile", "pos": [0, 256, 80], "rot": 0})
    layout.append({"asset_id": "walkway_tile", "pos": [160, 256, 80], "rot": 0})
    layout.append({"asset_id": "walkway_tile", "pos": [256, 0, 80], "rot": 90})
    layout.append({"asset_id": "walkway_tile", "pos": [256, 160, 80], "rot": 90})
    # Corner tile
    layout.append({"asset_id": "walkway_tile", "pos": [256, 256, 80], "rot": 0})

    # Railings
    layout.append({"asset_id": "railing_long", "pos": [39, 255, 80], "rot": 0})
    # Gap for stairs at X=260
    layout.append({"asset_id": "railing_long", "pos": [139, 255, 80], "rot": 0}) 
    layout.append({"asset_id": "railing_long", "pos": [255, -1, 80], "rot": 90})
    layout.append({"asset_id": "railing_long", "pos": [255, 159, 80], "rot": 90})

    # Stairs (Ascending North, flush against East wall)
    layout.append({"asset_id": "stairs", "pos": [265, 95, 0], "rot": 0}) 
    layout.append({"asset_id": "stair_railing", "pos": [264, 95, 0], "rot": 270}) 

    # Doors
    layout.append({"asset_id": "door", "pos": [311, 24, 0], "rot": 90})
    layout.append({"asset_id": "door", "pos": [84, 311, 80], "rot": 0})
    layout.append({"asset_id": "door", "pos": [204, 311, 80], "rot": 0})

    # Windows
    layout.append({"asset_id": "window", "pos": [82, 305, 68], "rot": 180})
    layout.append({"asset_id": "window", "pos": [210, 305, 68], "rot": 180})
    layout.append({"asset_id": "window", "pos": [305, 82, 68], "rot": 270})
    layout.append({"asset_id": "window", "pos": [305, 210, 68], "rot": 270})

    # Fireplace
    layout.append({"asset_id": "stone_fireplace", "pos": [300, 133, 0], "rot": 90})
    # Hearth Rug
    layout.append({"asset_id": "ornate_rug", "pos": [270, 145, 0.1], "rot": 90})

    # --- Bar Area ---
    layout.append({"asset_id": "bar_counter", "pos": [20, 274, 0], "rot": 0})
    layout.append({"asset_id": "shelf", "pos": [20, 309, 40], "rot": 0})
    
    # Back Bar (Kegs)
    layout.append({"asset_id": "barrel", "pos": [5, 265, 0], "rot": random.randint(0, 360)})
    layout.append({"asset_id": "barrel", "pos": [5, 285, 0], "rot": random.randint(0, 360)})
    layout.append({"asset_id": "barrel", "pos": [5, 305, 0], "rot": random.randint(0, 360)})

    for i in range(3):
        x = 27 + i * 20
        # Reduced jitter for stools
        rot_jitter = random.randint(-5, 5)
        pos_jitter = random.randint(-1, 1)
        layout.append({"asset_id": "barstool", "pos": [x + pos_jitter, 260 + pos_jitter, 0], "rot": rot_jitter})
        
        # More bar clutter
        layout.append({"asset_id": "bottle", "pos": [x + 4, 283, 38], "rot": random.randint(0, 360)})
        layout.append({"asset_id": "tankard", "pos": [x + 6, 281, 38], "rot": random.randint(0, 360)})
        if i % 2 == 0:
            layout.append({"asset_id": "candles", "pos": [x - 5, 283, 38], "rot": random.randint(0, 360)})

    # --- Under Stairs Storage ---
    # Stairs are at X=265. Area under them is X=265..305.
    # Y range 150..220 is mid-to-high clearance.
    layout.append({"asset_id": "barrel", "pos": [280, 180, 0], "rot": random.randint(0, 360)})
    layout.append({"asset_id": "barrel", "pos": [295, 195, 0], "rot": random.randint(0, 360)})
    layout.append({"asset_id": "barrel", "pos": [275, 210, 0], "rot": random.randint(0, 360)})
    # Stacked barrel
    layout.append({"asset_id": "barrel", "pos": [280, 180, 19], "rot": random.randint(0, 360)})

    # --- Table Groups ---
    def add_table_group(bx, by):
        layout.append({"asset_id": "ornate_rug", "pos": [bx + 9, by - 17, 0.1], "rot": 0})
        layout.append({"asset_id": "medieval_feast_table", "pos": [bx, by, 0], "rot": 0})
        
        # Jittery Chairs
        chairs = [
            (bx + 7, by + 21, 0), (bx + 43, by + 21, 0),
            (bx + 7, by - 3, 180), (bx + 43, by - 3, 180)
        ]
        for cx, cy, crot in chairs:
            rot_j = random.randint(-10, 10)
            layout.append({"asset_id": "chair", "pos": [cx + random.randint(-1,1), cy + random.randint(-1,1), 0], "rot": crot + rot_j})

        # Props Chaos (Constrained to table surface)
        # Force Candles for atmosphere
        layout.append({"asset_id": "candles", "pos": [bx + random.randint(15, 45), by + random.randint(10, 20), 24], "rot": random.randint(0, 360)})
        
        props = ["tankard", "mug", "bottle", "skull"]
        for _ in range(random.randint(2, 4)):
            px = bx + random.randint(10, 50)
            py = by + random.randint(5, 25)
            layout.append({"asset_id": random.choice(props), "pos": [px, py, 24], "rot": random.randint(0, 360)})
        
        # Lighting
        layout.append({"asset_id": "chandelier", "pos": [bx + 32, by + 16, 70], "rot": 0})

    def add_hearth_lounge(bx, by):
        # Cozy area near the fire
        layout.append({"asset_id": "ornate_rug", "pos": [bx, by - 20, 0.1], "rot": 90})
        
        # Chairs facing the fire (East is 90, so facing East is facing the fire)
        # Fireplace is at X=300. bx is approx 250.
        layout.append({"asset_id": "chair", "pos": [bx, by + 10, 0], "rot": 270 + random.randint(-15, 15)})
        layout.append({"asset_id": "chair", "pos": [bx, by - 30, 0], "rot": 270 + random.randint(-15, 15)})
        
        # Side table barrel
        layout.append({"asset_id": "barrel", "pos": [bx + 10, by - 10, 0], "rot": 0})
        layout.append({"asset_id": "bottle", "pos": [bx + 10, by - 10, 19], "rot": 0})
        layout.append({"asset_id": "mug", "pos": [bx + 5, by - 15, 19], "rot": 0})

    def add_captains_table(bx, by):
        # Double Rugs for status
        layout.append({"asset_id": "ornate_rug", "pos": [bx, by - 20, 0.1], "rot": 0})
        layout.append({"asset_id": "ornate_rug", "pos": [bx, by - 20, 0.2], "rot": 15}) # Slight offset
        
        # Rotated Table
        layout.append({"asset_id": "medieval_feast_table", "pos": [bx, by, 0], "rot": 90})
        
        # Chairs at Heads of table (North/South)
        # Table is 64x32. Rotated 90: Width=32 (X), Length=64 (Y).
        # Center is bx, by.
        # Ends are at Y+32 and Y-32 approx.
        layout.append({"asset_id": "chair", "pos": [bx + 10, by + 35, 0], "rot": 180})
        layout.append({"asset_id": "chair", "pos": [bx + 10, by - 35, 0], "rot": 0})
        # Side chairs
        layout.append({"asset_id": "chair", "pos": [bx - 20, by, 0], "rot": 270})
        layout.append({"asset_id": "chair", "pos": [bx + 40, by, 0], "rot": 90})

        # Hero Props
        layout.append({"asset_id": "skull", "pos": [bx + 10, by, 26], "rot": -15})
        layout.append({"asset_id": "candles", "pos": [bx + 10, by + 15, 26], "rot": 0})
        layout.append({"asset_id": "bottle", "pos": [bx + 10, by - 15, 26], "rot": 0})
        
        # Chandelier above
        layout.append({"asset_id": "chandelier", "pos": [bx + 16, by + 32, 70], "rot": 0})

    # Spread tables in the now open West/Center area
    # Original: add_table_group(60, 150)
    add_table_group(60, 150)
    # Original: add_captains_table(140, 150) -> This is in the middle of the room.
    # Let's shift it slightly South-East to clear the center for combat?
    # Or keep it, and place units around it?
    # The room is 320x320. Center is 160,160.
    # Entrance is at (160, 0) South? No, "Entrance Rug ... at [160, 40]".
    # So South is entrance. North is Mezzanine.
    # West is Bar. East is Fireplace.
    
    # Let's Move the Captains table towards the North-East to clear the center/South for entry combat.
    add_captains_table(200, 220) 
    
    # Entrance Rug (Welcome mat)
    layout.append({"asset_id": "ornate_rug", "pos": [160, 40, 0.1], "rot": 90})
    
    # Hearth Lounge
    add_hearth_lounge(250, 133)

    # --- Bard's Corner ---
    # NW area. X=40, Y=220.
    layout.append({"asset_id": "ornate_rug", "pos": [40, 220, 0.1], "rot": 45}) 
    layout.append({"asset_id": "chair", "pos": [40, 220, 0], "rot": 135}) 
    layout.append({"asset_id": "mug", "pos": [45, 215, 0], "rot": 0}) 

    # --- High Shelves (North Wall) ---
    for sx in [80, 140, 200]:
        layout.append({"asset_id": "shelf", "pos": [sx, 308, 60], "rot": 0})
        # Bottles on shelf
        layout.append({"asset_id": "bottle", "pos": [sx - 10, 308, 65], "rot": 0})
        layout.append({"asset_id": "bottle", "pos": [sx + 5, 308, 65], "rot": 0})
        layout.append({"asset_id": "candles", "pos": [sx + 15, 308, 65], "rot": 0})

    # Decorative Walls
    layout.append({"asset_id": "weapon_rack", "pos": [308, 100, 0], "rot": 90})
    layout.append({"asset_id": "trophy_wall", "pos": [160, 308, 40], "rot": 0})
    layout.append({"asset_id": "trophy_wall", "pos": [220, 308, 40], "rot": 0})

    # Barrels in corners
    layout.append({"asset_id": "barrel", "pos": [10, 10, 0], "rot": 0})
    layout.append({"asset_id": "barrel", "pos": [30, 15, 0], "rot": 45})
    
    # Spilled Drink
    layout.append({"asset_id": "tankard", "pos": [50, 260, 0], "rot": random.randint(0, 360)})

    # --- Post-Processing: Lights ---
    lights = []
    
    # Ambient settings
    ambient_color = {0.300, 0.300, 0.350} # Lua style string? No, json.
    
    # Add Fireplace Light
    lights.append({
        "position": [290, 133, 40],
        "color": [1.0, 0.6, 0.2],
        "intensity": 50.0, # 10x Boost
        "radius": 1500     # 10x Boost
    })

    for item in layout:
        aid = item["asset_id"]
        pos = item["pos"]
        
        if aid == "chandelier":
            # Hangs at Z=70 usually? Position in layout is the anchor?
            # Chandelier layout pos is [x, y, 70].
            # Light should be slightly below anchor.
            lights.append({
                "position": [pos[0], pos[1], pos[2] - 10],
                "color": [1.0, 0.95, 0.8],
                "intensity": 30.0, # 10x Boost
                "radius": 1200     # 10x Boost
            })
        elif aid == "candles":
            # Small point light
            lights.append({
                "position": [pos[0], pos[1], pos[2] + 5],
                "color": [1.0, 0.7, 0.4],
                "intensity": 8.0,  # 10x Boost
                "radius": 600      # 10x Boost
            })

    # --- Units ---
    # Team 1 (Heroes): South facing North (pi/2)
    t1_rot = 1.57
    team1_units = [
        [140, 60, 0, t1_rot],
        [160, 50, 0, t1_rot], # Point man
        [180, 60, 0, t1_rot]
    ]

    # Team 2 (Enemies): North facing South (-pi/2)
    t2_rot = -1.57
    team2_units = [
        [140, 190, 0, t2_rot],
        [160, 180, 0, t2_rot],
        [180, 190, 0, t2_rot]
    ]

    # --- Camera ---
    camera = {
        "eye": [160, -80, 300], # Looking from South-ish
        "center": [160, 200, 0],  # Looking at center of room
        "fov": 45 # Standard
    }

    # Final Output
    scene_def = {
        "layout": layout,
        "lights": lights,
        "team1_units": team1_units,
        "team2_units": team2_units,
        "camera": camera,
        "ambientColor": [0.2, 0.2, 0.3], # Night/Indoor feel
        "fogColor": [0.1, 0.1, 0.15],
        "fogNear": 300,
        "fogFar": 800
    }

    output_path = os.path.join(os.path.dirname(__file__), "../csg/tavern_layout.json")
    with open(output_path, "w") as f:
        json.dump(scene_def, f, indent=2)
    print(f"Generated layout with {len(layout)} items, {len(lights)} lights, and defined units.")

if __name__ == "__main__":
    create_layout()