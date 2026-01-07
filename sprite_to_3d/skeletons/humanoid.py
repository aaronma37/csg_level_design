class HumanoidSkeleton:
    """
    Defines the topology for the standard Humanoid V2 skeleton.
    Based on user specifications:
    - root (origin)
    - pelvis (center of mass)
    - spine (chest/shoulders)
    - head
    - Limbs (L/R): shoulder, elbow, hand, hip, knee, foot
    """
    
    # Topology: Bone Name -> Parent Name
    # 'root' has parent None
    TOPOLOGY = {
        "root": None,
        "pelvis": "root",
        "spine": "pelvis",
        "neck": "spine",
        "head": "neck",
        
        # Left Arm
        "shoulder_L": "spine",
        "elbow_L": "shoulder_L",
        "hand_L": "elbow_L",
        
        # Right Arm
        "shoulder_R": "spine",
        "elbow_R": "shoulder_R",
        "hand_R": "elbow_R",
        
        # Left Leg
        "hip_L": "pelvis",
        "knee_L": "hip_L",
        "foot_L": "knee_L",
        
        # Right Leg
        "hip_R": "pelvis",
        "knee_R": "hip_R",
        "foot_R": "knee_R",
    }

    # Valid height range (in voxels/pixels) for this skeleton to be applicable
    HEIGHT_RANGE = (45, 55)

    @classmethod
    def get_topology(cls):
        return cls.TOPOLOGY

    @classmethod
    def get_bones(cls):
        return list(cls.TOPOLOGY.keys())

    @classmethod
    def get_t_pose(cls, height):
        """
        Returns a dictionary of bone_name -> (x, y, z) coordinates.
        Scales a reference 50px tall humanoid to the requested height.
        """
        scale = height / 50.0
        
        # Reference positions for a 50-voxel tall humanoid (T-Pose)
        # Centered at X=0, Z=0. Y is up.
        ref_pose = {
            "root": (0, 0, 0),
            "pelvis": (0, 21, 0),
            "spine": (0, 32, 0),
            "neck": (0, 34, 0),
            "head": (0, 36, 0),
            
            # Left Arm (Extending +X)
            "shoulder_L": (6, 32, 0),
            "elbow_L": (13, 32, 0),
            "hand_L": (19, 32, 0),
            
            # Right Arm (Extending -X)
            "shoulder_R": (-6, 32, 0),
            "elbow_R": (-13, 32, 0),
            "hand_R": (-19, 32, 0),
            
            # Left Leg (Straight Down)
            "hip_L": (4, 21, 0),
            "knee_L": (4, 11, 0),
            "foot_L": (4, 0, 0),
            
            # Right Leg (Straight Down)
            "hip_R": (-4, 21, 0),
            "knee_R": (-4, 11, 0),
            "foot_R": (-4, 0, 0),
        }
        
        # Apply scaling
        scaled_pose = {}
        for bone, (x, y, z) in ref_pose.items():
            scaled_pose[bone] = (x * scale, y * scale, z * scale)
            
        return scaled_pose
