import json

with open("csg/asset_registry.json") as f:
    reg = json.load(f)

for k, v in reg.items():
    tags = v.get("asset_tags", [])
    if any(t in tags for t in ["furniture", "clutter", "decor", "light_source", "structure"]):
        print(f"{k}: {tags}")
