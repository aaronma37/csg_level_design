import json

def check():
    with open('sprite_to_3d/preview_v2/hero_rigged.json') as f:
        data = json.load(f)
        
    for part_name, part_data in data['parts'].items():
        if 'voxels' not in part_data or not part_data['voxels']:
            continue
            
        ys = [v[1] for v in part_data['voxels']]
        min_y, max_y = min(ys), max(ys)
        count = len(ys)
        
        print(f"Part {part_name}: {count} voxels. Y-Range: {min_y} to {max_y}")

if __name__ == "__main__":
    check()
