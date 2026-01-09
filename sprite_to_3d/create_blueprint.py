import json
import os
import sys

# Add current dir and parent to path for relative imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skeletons.mixamo import MixamoSkeleton

class UnitBlueprint:
    def __init__(self, name, skeleton_class, height):
        self.name = name
        self.skeleton_name = skeleton_class.__name__
        self.height = height
        self.skeleton_topology = skeleton_class.get_topology()
        self.bone_scales = {} # bone_name -> [sx, sy, sz]
        self.primitives = []

    def set_bone_scale(self, bone_name, sx, sy, sz):
        self.bone_scales[bone_name] = [sx, sy, sz]

    def add_primitive(self, primitive):
        self.primitives.append(primitive)

    def save(self, output_path):
        data = {
            "name": self.name,
            "skeleton": self.skeleton_name,
            "height": self.height,
            "topology": self.skeleton_topology,
            "bone_scales": self.bone_scales,
            "primitives": [p.to_dict() for p in self.primitives]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Blueprint saved to {output_path}")

if __name__ == "__main__":
    # Create a Mixamo Hero with custom proportions
    hero = UnitBlueprint("Hero_Mixamo", MixamoSkeleton, height=50)
    
    # Example: Make the head larger and the arms longer
    hero.set_bone_scale("mixamorig_Head", 1.4, 1.4, 1.4)
    hero.set_bone_scale("mixamorig_RightArm", 1.0, 1.2, 1.0)
    hero.set_bone_scale("mixamorig_LeftArm", 1.0, 1.2, 1.0)
    
    os.makedirs("blueprints", exist_ok=True)
    hero.save("blueprints/hero_mixamo.json")