import math
import numpy as np

class SDFBuilder:
    """
    Generates voxel coordinates using Signed Distance Functions.
    Ideal for organic shapes and smooth blending.
    """
    @staticmethod
    def sphere(p, radius):
        # p is [x, y, z]
        return np.linalg.norm(p) - radius

    @staticmethod
    def box(p, b):
        # b is [dx, dy, dz] half-extents
        q = np.abs(p) - b
        return np.linalg.norm(np.maximum(q, 0.0)) + min(max(q[0], max(q[1], q[2])), 0.0)

    @staticmethod
    def smooth_union(d1, d2, k):
        h = max(k - abs(d1 - d2), 0.0) / k
        return min(d1, d2) - h * h * k * (1.0 / 4.0)

    @staticmethod
    def generate_voxels(sdf_func, bounds_min, bounds_max, threshold=0.0):
        """
        Samples the SDF function over a grid and returns coordinates.
        """
        voxels = []
        for z in range(bounds_min[2], bounds_max[2]):
            for y in range(bounds_min[1], bounds_max[1]):
                for x in range(bounds_min[0], bounds_max[0]):
                    p = np.array([x, y, z], dtype=float)
                    # Translate p to be relative to the center of bounds for math ease
                    center = (np.array(bounds_min) + np.array(bounds_max)) / 2
                    dist = sdf_func(p - center)
                    
                    if dist <= threshold:
                        voxels.append((x, y, z))
        return voxels
