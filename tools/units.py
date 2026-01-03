# Semantic Scale Definitions (Character Units)
# Based on concepts/style_guide.md

CU = 50  # Character Unit: Standard character height in voxels

# Proportional Anchors
HEAD   = int(CU * 0.2)   # ~10v
WAIST  = int(CU * 0.5)   # ~25v
KNEE   = int(CU * 0.25)  # ~12v
SHOULDER = int(CU * 0.8) # ~40v

# Common Architectural Heights
DOOR_HEIGHT = int(CU * 1.2)  # 60v (A bit tight) or 70v per guide
DOOR_WIDTH  = int(CU * 0.6)  # 30v
TABLE_HEIGHT = WAIST
CHAIR_HEIGHT = KNEE

def to_voxels(cu_value):
    """Converts a CU decimal (0.5) to an integer voxel count."""
    return int(CU * cu_value)
