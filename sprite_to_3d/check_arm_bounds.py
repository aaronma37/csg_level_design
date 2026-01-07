import json

def check_x():
    with open('sprite_to_3d/preview_v2/hero_rigged.json') as f:
        data = json.load(f)
        
    for part_name in ["shoulder_L", "elbow_L", "hand_L", "shoulder_R", "elbow_R", "hand_R"]:
        if part_name not in data['parts']: continue
        voxels = data['parts'][part_name]['voxels']
        if not voxels: continue
        xs = [v[0] for v in voxels]
        print(f"Part {part_name}: X-Range: {min(xs)} to {max(xs)}")

if __name__ == "__main__":
    check_x()
