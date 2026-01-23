# Defines abstract Roles mapped to specific Tags
THEMES = {
    "tavern": {
        "floor_primary": {"include": ["floor", "wood"], "exclude": ["beveled"]},
        "floor_entrance": {"include": ["floor", "beveled"]}, # Visual marker for entrance
        "wall_north": {"include": ["wall", "north"], "exclude": ["doorway", "corner", "window", "mega"]},
        "wall_north_mega": {"include": ["wall", "north", "mega"]}, 
        "wall_west": {"include": ["wall", "north"], "exclude": ["doorway", "corner", "window", "mega"]}, 
        "wall_west_mega": {"include": ["wall", "north", "mega"]}, 
        "corner_nw": {"include": ["wall", "corner"]},
        "door_north": {"include": ["wall", "doorway", "north"]},
        "door_west": {"include": ["wall", "doorway", "north"]}, 
        "features_north": [
            {"include": ["furniture", "fireplace"], "type": "tile"}, 
            {"include": ["furniture", "bar", "mega"], "type": "tile"},
            {"include": ["wall", "north", "mega"], "type": "tile"}
        ],
        "features_central": [
            {"include": ["furniture", "table", "mega"], "type": "tile", "chance": 1.0, "count": 4} 
        ],
        "clutter": {"include": ["clutter"], "chance": 0.05}
    },
    "nature": {
        "floor_primary": {"include": ["floor", "grass"]},
        "floor_entrance": {"include": ["floor", "grass"]},
        "wall_north": {"include": ["nature", "cliff", "north"], "exclude": []}, 
        "wall_west": {"include": ["nature", "cliff", "north"], "exclude": []},
        "corner_nw": {"include": ["nature", "cliff", "corner"]},
        "door_north": {"include": ["nature", "path", "north"]}, 
        "door_west": {"include": ["nature", "path", "north"]},
        "features_north": [],
        "features_central": [],
        "clutter": {"include": ["flower", "patch"], "chance": 0.2}
    }
}