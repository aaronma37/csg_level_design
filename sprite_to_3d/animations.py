import math

class Animation:
    def __init__(self, duration_frames):
        self.duration = duration_frames

    def get_pose(self, frame):
        """Returns a dict of bone_name -> (rx, ry, rz) rotations in radians."""
        pass

class WalkAnimation(Animation):
    def get_pose(self, frame):
        t = (frame / self.duration) * 2 * math.pi
        
        # Sine-based walk cycle
        # rx: Forward/Backward swing
        # ry: Twist
        # rz: Side swing
        
        swing = math.sin(t) * 0.5 # +/- 30 degrees approx
        
        return {
            "hip_L": (swing, 0, 0),
            "knee_L": (max(0, -swing), 0, 0), # Simple knee bend
            "foot_L": (0, 0, 0),
            
            "hip_R": (-swing, 0, 0),
            "knee_R": (max(0, swing), 0, 0),
            "foot_R": (0, 0, 0),
            
            "shoulder_L": (-swing * 0.7, 0, 0), # Arms swing opposite to legs
            "elbow_L": (-0.2, 0, 0),
            
            "shoulder_R": (swing * 0.7, 0, 0),
            "elbow_R": (-0.2, 0, 0),
            
            "spine": (0, math.sin(t) * 0.1, 0), # Subtle torso twist
            "head": (0, -math.sin(t) * 0.1, 0)  # Counter-twist for head
        }

class IdleAnimation(Animation):
    def get_pose(self, frame):
        t = (frame / self.duration) * 2 * math.pi
        breath = math.sin(t) * 0.05
        return {
            "spine": (breath, 0, 0),
            "shoulder_L": (0, 0, breath),
            "shoulder_R": (0, 0, -breath)
        }
