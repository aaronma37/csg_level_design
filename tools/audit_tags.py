import json
import os
import glob

mappings = {
    "csg/bar_*.json": ["furniture", "habitable", "bar"],
    "csg/barstool.json": ["furniture", "habitable", "seating"],
    "csg/chair.json": ["furniture", "habitable", "seating"],
    "csg/door.json": ["furniture", "structure", "door"],
    "csg/window*.json": ["furniture", "structure", "window"],
    "csg/barrel.json": ["clutter", "decor", "storage"],
    "csg/base_*.json": ["rig_part", "unit"],
    "csg/character.json": ["unit"],
    "csg/pyromancer*.json": ["unit", "enemy"],
    "csg/figurine_hero.json": ["unit", "hero"],
    "csg/block_*.json": ["floor", "base", "block"],
    "csg/floor_*.json": ["floor", "base"],
    "csg/tile_*.json": ["floor", "base", "terrain"],
    "csg/grass_patch.json": ["nature", "outdoor", "decor"],
    "csg/flower_patch_*.json": ["nature", "outdoor", "decor"],
    "csg/shrub_small.json": ["nature", "outdoor", "decor"],
    "csg/reeds_patch.json": ["nature", "outdoor", "decor"],
    "csg/forest_*.json": ["nature", "outdoor", "structure"],
    "csg/collection_*.json": ["collection"],
    "csg/timber_wall_*.json": ["structure", "wall", "wood"],
    "csg/tavern_wall_*.json": ["structure", "wall", "interior"],
    "csg/timber_beam.json": ["structure", "wood"],
    "csg/wall_lantern_64.json": ["clutter", "decor", "light"],
    "csg/railing_*.json": ["structure", "railing"],
    "csg/stair*.json": ["structure", "stairs"],
    "csg/high_density_cave.json": ["terrain", "cave"],
    "csg/stocked_shelf_64.json": ["furniture", "storage"],
}

updated_count = 0
for pattern, tags in mappings.items():
    for filepath in glob.glob(pattern):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                # Migrate list-style collection to dict-style with tags
                new_data = {
                    "asset_tags": tags,
                    "layout": data
                }
                data = new_data
                updated_count += 1
            elif 'asset_tags' not in data or not data['asset_tags']:
                data['asset_tags'] = tags
                updated_count += 1
            else:
                continue
                
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error updating {filepath}: {e}")

print(f"Successfully updated {updated_count} files with asset_tags.")
