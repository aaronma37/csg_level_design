import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cv2
import numpy as np

def extract_colors(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None: return

    # Reshape to list of pixels
    pixels = img.reshape(-1, 4) if img.shape[2] == 4 else img.reshape(-1, 3)
    
from sklearn.cluster import KMeans

def extract_colors(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None: return

    pixels = img.reshape(-1, 4) if img.shape[2] == 4 else img.reshape(-1, 3)
    
    valid_pixels = []
    for p in pixels:
        if len(p) == 4 and p[3] < 10: continue
        valid_pixels.append((p[2], p[1], p[0])) # RGB
        
    if not valid_pixels: return
    
    # K-Means Clustering
    n_colors = 50
    kmeans = KMeans(n_clusters=n_colors, n_init=10)
    kmeans.fit(valid_pixels)
    colors = kmeans.cluster_centers_.astype(int)
    
    print("Found colors:")
    for i, c in enumerate(colors):
        print(f"    ({c[0]}, {c[1]}, {c[2]}), # {i+100}")

if __name__ == "__main__":

    extract_colors("../textures/character_spritesheet.png")
