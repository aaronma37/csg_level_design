import json
import math

def gen():
    duration = 90
    frames = []
    
    bones = [
        "spine", "neck", "head", 
        "shoulder_L", "elbow_L", "hand_L", 
        "shoulder_R", "elbow_R", "hand_R",
        "hip_L", "knee_L", "foot_L",
        "hip_R", "knee_R", "foot_R"
    ]

    for i in range(duration):
        frame = {}
        # Default all to 0
        for b in bones:
            frame[b] = [0, 0, 0]
            
        # Animate Left AND Right Arm
        # 0-30: X axis 0 to pi/2
        if i < 30:
            val = (i / 30.0) * (math.pi / 2)
            frame["shoulder_L"] = [val, 0, 0]
            frame["shoulder_R"] = [val, 0, 0]
        # 30-60: Y axis 0 to pi/2
        elif i < 60:
            val = ((i - 30) / 30.0) * (math.pi / 2)
            frame["shoulder_L"] = [0, val, 0]
            frame["shoulder_R"] = [0, val, 0]
        # 60-90: Z axis 0 to pi/2
        else:
            val = ((i - 60) / 30.0) * (math.pi / 2)
            frame["shoulder_L"] = [0, 0, val]
            frame["shoulder_R"] = [0, 0, val]
            
        frames.append(frame)

    output = {
        "duration": duration,
        "frames": frames
    }

    with open('sprite_to_3d/preview_v2/hero_anim.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("Generated Debug Animation (Left Arm Axis Test)")

if __name__ == "__main__":
    gen()
