import collections

def find_islands(voxels):
    """
    voxels: dict of (x,y,z) -> color_index
    Returns: list of sets, where each set is a connected island of voxel coordinates.
    """
    visited = set()
    islands = []
    
    keys = list(voxels.keys())
    
    for start_node in keys:
        if start_node in visited:
            continue
            
        # Start a new BFS
        current_island = set()
        queue = collections.deque([start_node])
        visited.add(start_node)
        
        while queue:
            node = queue.popleft()
            current_island.add(node)
            
            # Neighbors (6-connectivity)
            x, y, z = node
            for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
                neighbor = (x + dx, y + dy, z + dz)
                if neighbor in voxels and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        islands.append(current_island)
        
    return islands

def lint_model(voxels):
    """
    Performs validation on the voxel model.
    """
    if not voxels:
        print("Linter: Model is empty!")
        return False

    islands = find_islands(voxels)
    
    print(f"Linter Analysis:")
    print(f"  Total Voxels: {len(voxels)}")
    print(f"  Found {len(islands)} connected components.")
    
    if len(islands) > 1:
        # Sort islands by size
        islands.sort(key=len, reverse=True)
        main_size = len(islands[0])
        print(f"  WARNING: Found {len(islands)-1} floating islands!")
        for i, island in enumerate(islands[1:]):
            print(f"    Island {i+1}: {len(island)} voxels (Example: {list(island)[0]})")
        return False
    else:
        print("  SUCCESS: Model is fully connected.")
        return True

if __name__ == "__main__":
    # Test with the generated model if possible
    import sys
    import os
    # Add project root to path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # We could load from .vox, but let's assume we use this in the generation pipeline
    print("Linter script loaded.")
