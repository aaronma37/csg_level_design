import json
import math

def vec_sub(a, b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def normalize(v):
    m = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if m == 0: return [0,0,0]
    return [v[0]/m, v[1]/m, v[2]/m]

def analyze():
    with open('sprite_to_3d/preview_v2/hero_rigged.json') as f:
        data = json.load(f)
    
    rest = data['skeleton']['rest_pose']
    topo = data['skeleton']['topology']
    
    print("--- Skeleton Bone Vectors ---")
    for child, parent in topo.items():
        if parent:
            p1 = rest[child]
            p0 = rest[parent]
            v = vec_sub(p1, p0)
            vn = normalize(v)
            print(f"{parent} -> {child}: {v} (Dir: {vn[0]:.2f}, {vn[1]:.2f}, {vn[2]:.2f})")

if __name__ == "__main__":
    analyze()
