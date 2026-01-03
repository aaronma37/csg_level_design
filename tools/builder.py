class VoxelBuilder:
    """
    A logical voxel placement tool. 
    Better for LLMs to reason about 3D shapes than string-slicing.
    """
    def __init__(self):
        self.voxels = {} # (x, y, z) -> color_index

    def put(self, x, y, z, color):
        self.voxels[(int(x), int(y), int(z))] = int(color)

    def fill(self, x1, y1, z1, x2, y2, z2, color):
        """Inclusive box fill."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.put(x, y, z, color)

    def line(self, x1, y1, z1, x2, y2, z2, color):
        """Draws a simple line of voxels."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        dz = abs(z2 - z1)
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        step_z = 1 if z1 < z2 else -1
        
        # Max steps
        n = max(dx, dy, dz)
        if n == 0:
            self.put(x1, y1, z1, color)
            return

        for i in range(n + 1):
            x = x1 + (i * dx // n) * step_x
            y = y1 + (i * dy // n) * step_y
            z = z1 + (i * dz // n) * step_z
            self.put(x, y, z, color)

    def carve(self, x1, y1, z1, x2, y2, z2):
        """Inclusive box subtraction."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    key = (int(x), int(y), int(z))
                    if key in self.voxels:
                        del self.voxels[key]

    def mirror_x(self):
        """Mirrors all voxels from positive X to negative X."""
        new_voxels = {}
        for (x, y, z), color in self.voxels.items():
            if x >= 0:
                new_voxels[(x, y, z)] = color
                if x > 0:
                    new_voxels[(-x, y, z)] = color
        self.voxels = new_voxels

    def add_component(self, other_voxels, ox=0, oy=0, oz=0):
        """Merges voxels from another builder or dict with an offset."""
        # other_voxels can be a VoxelBuilder or a dict
        src = other_voxels.voxels if hasattr(other_voxels, 'voxels') else other_voxels
        for (x, y, z), color in src.items():
            self.put(x + ox, y + oy, z + oz, color)

    def rotate_z(self, steps=1):
        """Rotates all current voxels around Z axis in 90-degree steps."""
        for _ in range(steps % 4):
            new_voxels = {}
            for (x, y, z), color in self.voxels.items():
                new_voxels[(-y, x, z)] = color
            self.voxels = new_voxels

    def get_instructions(self):
        # Group by color for the compiler
        by_color = {}
        for (x, y, z), color in self.voxels.items():
            if color not in by_color:
                by_color[color] = []
            by_color[color].append([x, y, z])
            
        instructions = []
        for color, points in by_color.items():
            instructions.append({
                "op": "add",
                "shape": "point_cloud",
                "pos": [0, 0, 0],
                "points": points,
                "color": color
            })
        return instructions
