import cv2
import numpy as np

def analyze_alignment(image_path):
    img = cv2.imread(image_path)
    if img is None: return

    width = img.shape[1]
    half_width = width // 2
    
    real_img = img[:, :half_width]
    rend_img = img[:, half_width:]
    
    # Convert to grayscale
    real_gray = cv2.cvtColor(real_img, cv2.COLOR_BGR2GRAY)
    rend_gray = cv2.cvtColor(rend_img, cv2.COLOR_BGR2GRAY)
    
    # Threshold (assuming object is dark on light background)
    # Background is white (255).
    _, real_mask = cv2.threshold(real_gray, 200, 255, cv2.THRESH_BINARY_INV)
    _, rend_mask = cv2.threshold(rend_gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate Centroids
    M_real = cv2.moments(real_mask)
    M_rend = cv2.moments(rend_mask)
    
    cx_real = int(M_real["m10"] / M_real["m00"]) if M_real["m00"] > 0 else 0
    cy_real = int(M_real["m01"] / M_real["m00"]) if M_real["m00"] > 0 else 0
    
    cx_rend = int(M_rend["m10"] / M_rend["m00"]) if M_rend["m00"] > 0 else 0
    cy_rend = int(M_rend["m01"] / M_rend["m00"]) if M_rend["m00"] > 0 else 0
    
    print(f"Analysis of {image_path}:")
    print(f"  Real Object Center: ({cx_real}, {cy_real})")
    print(f"  Rend Object Center: ({cx_rend}, {cy_rend})")
    print(f"  X-Offset: {cx_rend - cx_real} pixels")
    print(f"  Y-Offset: {cy_rend - cy_real} pixels")

if __name__ == "__main__":
    analyze_alignment("debug_frame_0.png")
    analyze_alignment("debug_frame_48.png")
