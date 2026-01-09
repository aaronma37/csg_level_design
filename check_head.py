import json
import os

rig_path = "sprite_to_3d/actor_assets/hero/rig.json"
if not os.path.exists(rig_path):
    print(f"{rig_path} not found")
    exit(1)

with open(rig_path, "r") as f:
    data = json.load(f)

head = data["parts"].get("mixamorig_Head", {"voxels": []})
print(f"Head Voxel Count: {len(head['voxels'])}")

if head["voxels"]:
    xs = [v[0] for v in head["voxels"]]
    ys = [v[1] for v in head["voxels"]]
    zs = [v[2] for v in head["voxels"]]
    print(f"X Range: {min(xs)} to {max(xs)} (Size: {max(xs)-min(xs)+1})")
    print(f"Y Range: {min(ys)} to {max(ys)} (Size: {max(ys)-min(ys)+1})")
    print(f"Z Range: {min(zs)} to {max(zs)} (Size: {max(zs)-min(zs)+1})")

# Check if other bones have head voxels
for bone, bdata in data["parts"].items():
    if bone == "mixamorig_Head": continue
    if not bdata["voxels"]: continue
    v0 = bdata["voxels"][0]
    # Head is high up, usually Y > 30 in world space
    # Let's see if we can find them
    pass
