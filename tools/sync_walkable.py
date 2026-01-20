import os
import re

TILES_DIR = "csg_assets/tiles"

for filename in os.listdir(TILES_DIR):
    if not filename.endswith(".lua"):
        continue
    
    filepath = os.path.join(TILES_DIR, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if nav_mask is 1
    # Matches: nav_mask = 1 (allowing for whitespace)
    is_walkable = re.search(r'nav_mask\s*=\s*1', content)
    
    if is_walkable:
        # Find tile_tags = { ... }
        tags_match = re.search(r'tile_tags\s*=\s*\{([^}]+)\}', content)
        if tags_match:
            tags_str = tags_match.group(1)
            # Check if "walkable" is already there
            if '"walkable"' not in tags_str and "'walkable'" not in tags_str:
                # Add "walkable"
                new_tags_str = tags_str.strip()
                if new_tags_str and not new_tags_str.endswith(','):
                    new_tags_str += ', '
                new_tags_str += '"walkable"'
                
                new_content = content.replace(tags_str, new_tags_str)
                with open(filepath, 'w') as f:
                    f.write(new_content)
                print(f"Added 'walkable' to {filename}")
        else:
            # Handle case where tile_tags might be missing but nav_mask=1
            # (Adding to metadata block)
            meta_match = re.search(r'metadata\s*=\s*\{', content)
            if meta_match:
                insertion = 'tile_tags = {"walkable"}, '
                new_content = content.replace(meta_match.group(0), meta_match.group(0) + insertion)
                with open(filepath, 'w') as f:
                    f.write(new_content)
                print(f"Created tile_tags with 'walkable' for {filename}")

