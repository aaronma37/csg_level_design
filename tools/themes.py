# Defines abstract Roles mapped to specific Tags
THEMES = {
    "tavern": {
        "floor_primary": {"include": ["floor", "wood"], "exclude": ["beveled"]},
        "floor_entrance": {"include": ["floor", "beveled"]}, # Visual marker for entrance
        "wall_north": {"include": ["wall", "north", "v2"], "exclude": ["doorway", "corner", "window"]},
        "wall_west": {"include": ["wall", "north", "v2"], "exclude": ["doorway", "corner", "window"]}, # Will be rotated
        "corner_nw": {"include": ["wall", "corner"]},
        "door_north": {"include": ["wall", "doorway", "north"]},
        "door_west": {"include": ["wall", "doorway", "north"]}, # Will be rotated
        "features_north": [
            {"include": ["furniture", "fireplace"], "type": "tile"}, 
            {"include": ["furniture", "bar", "mega"], "type": "tile"}
        ],
        "clutter": {"include": ["clutter"], "chance": 0.05}
    },
    "nature": {
        "floor_primary": {"include": ["floor", "grass"]},
        "floor_entrance": {"include": ["floor", "grass"]},
        "wall_north": {"include": ["nature", "cliff", "north"], "exclude": []}, # Hypothetical
        "wall_west": {"include": ["nature", "cliff", "north"], "exclude": []},
        "corner_nw": {"include": ["nature", "cliff", "corner"]},
        "door_north": {"include": ["nature", "path", "north"]}, # Hypothetical
        "door_west": {"include": ["nature", "path", "north"]},
        "features_north": [],
        "clutter": {"include": ["flower", "patch"], "chance": 0.2}
    }
}
