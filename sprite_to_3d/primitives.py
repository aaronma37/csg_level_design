class Primitive:
    """
    Base class for semantic attachments to a skeleton.
    These are NOT voxel definitions yet, but schema definitions.
    """
    def __init__(self, name, parent_bone, primitive_type, **kwargs):
        self.name = name
        self.parent_bone = parent_bone
        self.primitive_type = primitive_type
        self.params = kwargs

    def to_dict(self):
        return {
            "name": self.name,
            "parent_bone": self.parent_bone,
            "type": self.primitive_type,
            "params": self.params
        }

class StaticMeshPrimitive(Primitive):
    """
    Represents a rigid object (helmet, shoulderpad).
    """
    def __init__(self, name, parent_bone, shape="box", dimensions=(1,1,1), offset=(0,0,0)):
        super().__init__(name, parent_bone, "static_mesh", 
                         shape=shape, 
                         dimensions=dimensions, 
                         offset=offset)

class RibbonPrimitive(Primitive):
    """
    Represents a flowing object (cape, hair).
    """
    def __init__(self, name, parent_bone, length=10, width=5, flexibility=0.8):
        super().__init__(name, parent_bone, "ribbon", 
                         length=length, 
                         width=width, 
                         flexibility=flexibility)
