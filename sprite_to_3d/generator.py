import json
import math
import sys
import os
from PIL import Image

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skeletons.humanoid import HumanoidSkeleton
from tools.builder import VoxelBuilder
import palette

class VoxelGenerator:
    def __init__(self, blueprint_path):
        with open(blueprint_path, 'r') as f:
            self.blueprint = json.load(f)
            
        self.height = self.blueprint['height']
        self.builder = VoxelBuilder()
        self.voxel_owners = {} # (x,y,z) -> bone_name
        self.pose = HumanoidSkeleton.get_t_pose(self.height)
        self.palette_map = self._load_palette()
        
    def _load_palette(self):
        # Inverse map: (r,g,b) -> index
        pmap = {}
        for idx, color in enumerate(palette.PALETTE_COLORS):
            if len(color) == 4 and color[3] == 0: continue # Skip transparent
            rgb = (color[0], color[1], color[2])
            pmap[rgb] = idx
        return pmap

    def _get_closest_color(self, r, g, b):
        # Simple Euclidean distance
        best_idx = 0
        min_dist = float('inf')
        for idx, color in enumerate(palette.PALETTE_COLORS):
            if idx == 0: continue
            pr, pg, pb = color[0], color[1], color[2]
            dist = (r-pr)**2 + (g-pg)**2 + (b-pb)**2
            if dist < min_dist:
                min_dist = dist
                best_idx = idx
        return best_idx

    def draw_tapered_capsule(self, p1, p2, r1, r2, color_idx, owner_bone):
        """Draws a capsule with different start/end radii."""
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        
        dx, dy, dz = x2-x1, y2-y1, z2-z1
        length_sq = dx*dx + dy*dy + dz*dz
        length = math.sqrt(length_sq)
        
        if length == 0:
            return

        # Raymarching steps
        steps = int(length * 2) + 1
        
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            cx = x1 + dx * t
            cy = y1 + dy * t
            cz = z1 + dz * t
            
            # Interpolate radius
            cur_r = r1 + (r2 - r1) * t
            r_int = int(math.ceil(cur_r))
            r2_sq = cur_r * cur_r
            
            for ox in range(-r_int, r_int+1):
                for oy in range(-r_int, r_int+1):
                    for oz in range(-r_int, r_int+1):
                        if ox*ox + oy*oy + oz*oz <= r2_sq:
                            vx, vy, vz = int(cx + ox), int(cy + oy), int(cz + oz)
                            self.builder.put(vx, vy, vz, color_idx)
                            self.voxel_owners[(vx, vy, vz)] = owner_bone

    def generate_base_body(self):
        topology = self.blueprint['topology']
        
        # Define thickness for body parts (Start Radius, End Radius)
        # Parent -> Child
        radius_map = {
            "spine": (3.5, 3.0),     # Spine -> Head (neck area)
            "pelvis": (3.0, 3.5),    # Pelvis -> Spine
            "shoulder": (2.2, 1.8),  # Shoulder -> Elbow
            "elbow": (1.8, 1.2),     # Elbow -> Hand
            "hip": (2.5, 2.0),       # Hip -> Knee
            "knee": (2.0, 1.5),      # Knee -> Foot
        }
        
        # Default color (Skin tone - usually around index 45-50 in standard palettes, using 48 as placeholder)
        base_color = 48 

        for bone, parent in topology.items():
            if parent is None: continue
            
            # Skip drawing the logical root connection (it creates a 'third leg' pillar)
            if parent == "root": continue
            
            p1 = self.pose[parent]
            p2 = self.pose[bone]
            
            # Determine radius based on connection
            r1, r2 = (2.0, 2.0)
            
            # Check based on parent bone name (source of the limb segment)
            for key, radii in radius_map.items():
                if key in parent:
                    r1, r2 = radii
                    break
            
            # Special case for Head: Parent is Spine. 
            # We want to draw the HEAD volume, not the neck.
            # The topology edge "spine" -> "head" is the neck.
            # We should draw the head explicitly at the 'head' position?
            # Or treat the bone as the volume?
            # Current logic draws edges.
            
            if bone == "head":
                # Draw Neck
                self.draw_tapered_capsule(p1, p2, 4.0, 3.5, base_color, "neck") # neck is part of spine usually, but let's label it neck
                # Draw Head Volume explicitly
                hx, hy, hz = p2
                # Sphere for head
                self.draw_tapered_capsule((hx, hy, hz), (hx, hy+7, hz), 4.5, 4.0, base_color, "head")
            else:
                # Use the bone name as the owner
                self.draw_tapered_capsule(p1, p2, r1, r2, base_color, bone)

    def generate_primitives(self):
        for prim in self.blueprint['primitives']:
            ptype = prim['type']
            bone = prim['parent_bone']
            bx, by, bz = self.pose[bone]
            
            if ptype == "static_mesh":
                # Box logic
                dims = prim['params']['dimensions']
                off = prim['params']['offset']
                dx, dy, dz = dims
                ox, oy, oz = off
                
                # Center box on bone + offset
                x1 = int(bx + ox - dx/2)
                y1 = int(by + oy - dy/2)
                z1 = int(bz + oz - dz/2)
                
                self.builder.fill(x1, y1, z1, x1+int(dx), y1+int(dy), z1+int(dz), 25) # 25 = Metal/Stone placeholder

            elif ptype == "ribbon":
                # Simple downward ribbon
                length = int(prim['params']['length'])
                width = int(prim['params']['width'])
                
                for y in range(length):
                    for x in range(width):
                        # Centered on bone X, extending down Y, offset back Z
                        px = int(bx - width/2 + x)
                        py = int(by - y)
                        pz = int(bz - 2) # Behind back
                        self.builder.put(px, py, pz, 150) # 150 = Cloth placeholder

    def find_skin_color(self, img, region):
        """
        Heuristic: Find the most frequent 'warm' color in the region.
        Assumes standard humanoid skin (R > B, R > G).
        """
        pixels = img.load()
        width, height = img.size
        y_start, y_end = region
        
        color_counts = {}
        
        for y in range(y_start, y_end):
            if y >= height: break
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a < 128: continue
                
                # Heuristic: Skin is usually Warm (Red dominant)
                # Skip if Blue is the dominant channel (Purple, Blue clothes)
                if b > r or b > g: continue
                
                # Skip if Green is dominant (Green clothes)
                if g > r: continue
                
                # Skip dark outlines
                if r < 50: continue
                
                rgb = (r, g, b)
                color_counts[rgb] = color_counts.get(rgb, 0) + 1
        
        if not color_counts:
            print("No skin tone found with heuristics. Defaulting.")
            return (200, 150, 100) # Fallback skin tone
            
        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda item: item[1], reverse=True)
        return sorted_colors[0][0]

    def symbolic_paint(self, texture_path):
        try:
            img = Image.open(texture_path).convert("RGBA")
            sprite = img.crop((0, 0, 64, 64))
        except:
            print("Texture load failed")
            return

        # 1. Neuro/Analysis Step: Extract Skin Tone from Face Region
        # We look at the head area but filter for "skin-like" colors
        skin_rgb = self.find_skin_color(sprite, (14, 28))
        skin_idx = self._get_closest_color(*skin_rgb)
        print(f"Extracted Skin Tone: {skin_rgb} -> Index {skin_idx}")

        # 2. Paint Everything with Skin Tone (Mannequin Style)
        # The user requested the "entire sprite" be this color for the base body.
        for (vx, vy, vz) in self.builder.voxels.keys():
            self.builder.put(vx, vy, vz, skin_idx)

    def save_vox(self, output_path):
        import scene_composer
        from linter import lint_model
        
        print("Running Linter...")
        lint_model(self.builder.voxels)
        
        writer = scene_composer.VoxWriter()
        
        # Re-pack into list expected by VoxWriter
        # VoxWriter expects (x, y, z, c) tuples
        # Let's transform coordinates to be safe
        packed_voxels = []
        for (x, y, z), c in self.builder.voxels.items():
            packed_voxels.append((x, z, y, c))
            
        model_idx = writer.add_model(packed_voxels)
        
        # Create a default instance at (0,0,0) with no rotation
        # scene_instances: list of (model_index, pos, rot, name)
        # pos is (x, y, z)
        instances = [(model_idx, (0, 0, 0), 0, "hero")]
        
        writer.save(output_path, instances)
            
        print(f"Saved {len(self.builder.voxels)} voxels to {output_path}")

if __name__ == "__main__":
    gen = VoxelGenerator("blueprints/hero_naked.json")
    print("Generating Base Body...")
    gen.generate_base_body()
    # gen.generate_primitives() # Naked for now
    print("Painting Symbolically...")
    gen.symbolic_paint("textures/character_spritesheet.png")
    
    os.makedirs("output", exist_ok=True)
    gen.save_vox("output/hero_gen.vox")
