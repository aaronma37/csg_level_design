import cv2
import sys

def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    indices = [0, total_frames//4, total_frames//2, 3*total_frames//4]
    
    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            filename = f"debug_frame_{i}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename} (Frame {idx})")
            
    cap.release()

if __name__ == "__main__":
    extract_frames(sys.argv[1])
