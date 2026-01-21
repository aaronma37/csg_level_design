import os

# Project Root is two levels up from this file (tools/project.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Key Directories
CSG_DIR = os.path.join(PROJECT_ROOT, "csg")
GENERATORS_DIR = os.path.join(PROJECT_ROOT, "generators")
TILES_DIR = os.path.join(PROJECT_ROOT, "csg_assets", "tiles")
VOX_DIR = os.path.join(PROJECT_ROOT, "vox")

# Deployment Target (External to repo)
GAME_ASSETS_DIR = os.path.expanduser("~/love_exp/assets/csg_assets")

def get_asset_path(asset_name: str) -> str:
    """Returns the absolute path to a CSG JSON file."""
    return os.path.join(CSG_DIR, f"{asset_name}.json")

def get_tile_path(tile_filename: str) -> str:
    """Returns the absolute path to a Tile Lua file."""
    return os.path.join(TILES_DIR, tile_filename)

def ensure_dirs():
    """Ensures all key directories exist."""
    for d in [CSG_DIR, GENERATORS_DIR, TILES_DIR, VOX_DIR]:
        os.makedirs(d, exist_ok=True)
