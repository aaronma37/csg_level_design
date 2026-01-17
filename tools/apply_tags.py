import os
import glob
import json

def get_auto_tags(name):
    tags = set()
    name = name.lower()

    # --- Floor ---
    if any(x in name for x in ['floor', 'walkway', 'grass', 'terrain', 'road', 'ground', 'plateau', 'meadow', 'river', 'cliff']):
        tags.add('floor')
        # Cliffs are tricky, usually walls, but top is floor. 
        # Let's assume tiles named 'plateau' are floor.
    
    # --- Light Sources ---
    if any(x in name for x in ['candle', 'chandelier', 'lamp', 'fire', 'light']):
        tags.add('light_source')

    # --- Occluders (Solid Objects) ---
    # Default assumption: Most things are occluders unless specified.
    # But let's be specific for the "Large Occluder" request.
    if any(x in name for x in ['wall', 'pillar', 'barrel', 'crate', 'table', 'shelf', 'counter', 'rock', 'tree', 'stump', 'rack', 'stairs']):
        tags.add('occluder')

    # --- Passable / Decoration (Not Occluders) ---
    # Rugs, small debris, spilled drinks
    if any(x in name for x in ['rug', 'debris', 'tankard', 'mug', 'bottle', 'skull', 'flower']):
        tags.add('passable')
        if 'occluder' in tags: tags.remove('occluder')

    # Special Case: Fireplace is both light and occluder
    if 'fireplace' in name:
        tags.add('occluder')
        tags.add('light_source')
        
    # Special Case: Stairs
    # They are walkable (floor-ish) but also fill volume. 
    # For spawning check, we don't want to spawn INSIDE the step blocks.
    if 'stairs' in name:
        tags.add('occluder')
        # Also maybe 'floor' if we want to allow spawning ON them? 
        # For now, let's keep them as occluder to prevent spawning in the middle of a staircase.

    return list(tags)

def tag_assets():
    csg_dir = "csg"
    files = glob.glob(os.path.join(csg_dir, "*.json"))
    
    count = 0
    for filepath in files:
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {filepath}")
                continue
        
        # Skip collections (lists) - we tag leaf assets (dicts)
        if isinstance(data, list):
            continue
            
        current_tags = set(data.get('tags', []))
        new_tags = set(get_auto_tags(os.path.basename(filepath)))
        
        # Merge? Or Overwrite?
        # Let's merge for now, prioritizing existing.
        # actually, since this is first run, let's trust the auto-tagger but preserve manual ones if they existed?
        # Assuming no manual tags exist yet.
        
        final_tags = list(current_tags.union(new_tags))
        final_tags.sort()
        
        if final_tags != data.get('tags', []):
            data['tags'] = final_tags
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Tagged {os.path.basename(filepath)}: {final_tags}")
            count += 1
            
    print(f"Updated tags for {count} assets.")

if __name__ == "__main__":
    tag_assets()
