import json
import os
from skeletons.humanoid import HumanoidSkeleton
from primitives import StaticMeshPrimitive, RibbonPrimitive

class UnitBlueprint:
    def __init__(self, name, skeleton_class, height):
        self.name = name
        self.skeleton_name = skeleton_class.__name__
        self.height = height
        self.skeleton_topology = skeleton_class.get_topology()
        self.primitives = []

    def add_primitive(self, primitive):
        self.primitives.append(primitive)

    def save(self, output_path):
        data = {
            "name": self.name,
            "skeleton": self.skeleton_name,
            "height": self.height,
            "topology": self.skeleton_topology,
            "primitives": [p.to_dict() for p in self.primitives]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Blueprint saved to {output_path}")

if __name__ == "__main__":
    # Create Naked Hero for base body verification
    hero = UnitBlueprint("Hero_Naked", HumanoidSkeleton, height=50)
    
    # No primitives added!
    
    os.makedirs("blueprints", exist_ok=True)
    hero.save("blueprints/hero_naked.json")