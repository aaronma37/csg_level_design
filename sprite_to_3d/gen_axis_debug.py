import json
import math
import sys
import os

def gen():
    # 3 Phases: X, Y, Z
    # Each phase: 30 frames.
    # 0-10: Rest
    # 10-20: Rotate 0 -> 90
    # 20-30: Rotate 90 -> 0
    
    phases = ["X (Twist?)", "Y (Swing?)", "Z (Abduct?)"]
    duration_per_phase = 40
    total_duration = duration_per_phase * 3
    
    frames = []
    
    bones = [
        "spine", "neck", "head", 
        "shoulder_L", "elbow_L", "hand_L", 
        "shoulder_R", "elbow_R", "hand_R",
        "hip_L", "knee_L", "foot_L",
        "hip_R", "knee_R", "foot_R"
    ]

    for i in range(total_duration):
        frame = {}
        for b in bones:
            frame[b] = [0, 0, 0]
            
        phase_idx = i // duration_per_phase
        local_t = i % duration_per_phase
        
        angle = 0
        if 10 <= local_t < 20:
            angle = ((local_t - 10) / 10.0) * (math.pi / 2)
        elif 20 <= local_t < 30:
            angle = (1.0 - (local_t - 20) / 10.0) * (math.pi / 2)
            
        # Apply to Left Arm
        # Rest Pose: (6, 32, 0) -> Extending +X
        
        rot = [0, 0, 0]
        if phase_idx == 0: # Rotate X
            rot = [angle, 0, 0]
        elif phase_idx == 1: # Rotate Y
            rot = [0, angle, 0]
        elif phase_idx == 2: # Rotate Z
            rot = [0, 0, angle]
            
        frame["shoulder_L"] = rot
        
        # Mirror for Right Arm (check symmetry)
        # frame["shoulder_R"] = rot 
        
        frames.append(frame)

    output = {
        "duration": total_duration,
        "frames": frames,
        "debug_notes": "0-40: X-Axis (Twist), 40-80: Y-Axis (Swing Fwd), 80-120: Z-Axis (Abduct Up/Down)"
    }

    out_path = 'sprite_to_3d/preview_v2/hero_anim.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Generated Axis Debug Animation to {out_path}")
    print("Run './sprite_to_3d/run_preview.sh' to view.")

if __name__ == "__main__":
    gen()
