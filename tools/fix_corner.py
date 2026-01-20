import json
path = "csg/corner_pillar.json"
with open(path, 'r') as f:
    data = json.load(f)
for inst in data['instructions']:
    if 'size' in inst and inst['size'][2] >= 60:
        inst['size'][2] = 96
        inst['pos'][2] = 48
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
