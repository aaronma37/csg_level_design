import sys
import struct
import numpy as np
import scipy.cluster.vq
import argparse

def load_obj(path):
    vertices = []
    colors = []
    faces = []
    
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            
            if parts[0] == 'v':
                # Parse vertex: v x y z [r g b]
                raw_v = [float(x) for x in parts[1:4]]
                # Swap Y and Z for coordinate system conversion (Y-up to Z-up)
                v = [raw_v[0], raw_v[2], raw_v[1]]
                vertices.append(v)
                
                if len(parts) >= 7:
                    # Has color
                    c = [float(x) for x in parts[4:7]]
                    colors.append(c)
                else:
                    # Default white
                    colors.append([1.0, 1.0, 1.0])
                    
            elif parts[0] == 'f':
                # Parse face: f v1/vt1/vn1 ...
                # OBJ is 1-indexed
                face_indices = []
                for p in parts[1:]:
                    idx = int(p.split('/')[0]) - 1
                    face_indices.append(idx)
                
                # Triangulate polygon fan
                for i in range(1, len(face_indices) - 1):
                    faces.append([face_indices[0], face_indices[i], face_indices[i+1]])

    return np.array(vertices), np.array(colors), np.array(faces)

def get_voxel_grid(vertices, colors, faces, resolution):
    # 1. Normalize and scale vertices to [0, resolution]
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    dims = maxs - mins
    max_dim = dims.max()
    
    if max_dim == 0:
        scale = 1.0
    else:
        # Leave a 1-voxel padding
        scale = (resolution - 2) / max_dim
        
    # Center the model
    center = (mins + maxs) / 2
    offset = np.array([resolution/2, resolution/2, resolution/2]) - center * scale
    
    scaled_verts = vertices * scale + offset
    
    # 2. Rasterize via Sampling
    # Store (min_dist_sq, color) for each voxel
    # We want the color of the point closest to the voxel center
    voxel_map = {} 
    
    print("Rasterizing triangles...")
    
    # Check color range and stats
    max_c = colors.max()
    min_c = colors.min()
    mean_c = colors.mean()
    print(f"Color range: {min_c} - {max_c}, Mean: {mean_c}")
    
    if max_c > 1.0:
        if max_c > 200 or mean_c > 1.0:
            print("Normalizing colors 0-255 -> 0-1")
            colors /= 255.0
        else:
            print("Found values > 1.0 but mean is low. Clamping to 0-1 range (assuming outliers).")
            colors = np.clip(colors, 0, 1.0)
        
    for face in faces:
        v0, v1, v2 = scaled_verts[face]
        c0, c1, c2 = colors[face]
        
        # Vector edge lengths
        e0 = v1 - v0
        e1 = v2 - v0
        
        # Area in grid units (approx)
        cross = np.cross(e0, e1)
        area = 0.5 * np.linalg.norm(cross)
        
        # Sample density
        # Increase density to ensure we hit the center vicinity
        num_samples = int(max(1, area * 20)) 
        
        r1 = np.sqrt(np.random.random(num_samples))
        r2 = np.random.random(num_samples)
        
        u = 1 - r1
        v = r1 * (1 - r2)
        w = r1 * r2
        
        points = np.outer(u, v0) + np.outer(v, v1) + np.outer(w, v2)
        point_colors = np.outer(u, c0) + np.outer(v, c1) + np.outer(w, c2)
        
        # Quantize to integer voxel coords
        coords = np.floor(points).astype(int)
        
        # Calculate squared distance to voxel center (coords + 0.5)
        # points - (coords + 0.5)
        centers = coords + 0.5
        dists_sq = np.sum((points - centers)**2, axis=1)
        
        for i in range(num_samples):
            x, y, z = coords[i]
            if 0 <= x < resolution and 0 <= y < resolution and 0 <= z < resolution:
                key = (x, y, z)
                d_sq = dists_sq[i]
                
                if key not in voxel_map:
                    voxel_map[key] = (d_sq, point_colors[i])
                else:
                    # Update if closer to center
                    if d_sq < voxel_map[key][0]:
                        voxel_map[key] = (d_sq, point_colors[i])

    # Extract just the colors
    final_map = {k: v[1] for k, v in voxel_map.items()}
    return final_map

def write_string(s):
    b = s.encode('ascii')
    return struct.pack('<I', len(b)) + b

def write_dict(d):
    # d is a dict of strings
    b = struct.pack('<I', len(d))
    for k, v in d.items():
        b += write_string(k)
        b += write_string(v)
    return b

def write_chunk(id, content):
    return id.encode('ascii') + struct.pack('<II', len(content), 0) + content

def write_vox(voxel_map, filename, resolution, gamma=2.2, quantize=24, saturation=1.0, max_colors=255, delight=False):
    # 1. Extract unique colors and build palette
    unique_voxels = []
    
    # Efficiently collect all colors
    voxel_items = list(voxel_map.items())
    if not voxel_items:
        print("No voxels generated!")
        return

    # Unpack keys and values in strict order
    keys = [k for k, v in voxel_items]
    all_colors = [v for k, v in voxel_items]

    pixels = np.array(all_colors) # (N, 3) floats 0-1
    
    print(f"Sample raw colors: {pixels[:5]}")
    
    # 1. Gamma Correction
    if gamma != 1.0:
        print(f"Applying Gamma {gamma} correction...")
        pixels = np.power(np.clip(pixels, 0, 1), 1.0/gamma)

    # 2. Saturation Adjustment
    if saturation != 1.0:
        print(f"Applying Saturation {saturation}...")
        # Convert to HSV/luminance or simple Lerp towards grayscale
        # Simple luminance method
        # lum = 0.299*R + 0.587*G + 0.114*B
        lum = np.dot(pixels, np.array([0.299, 0.587, 0.114]))
        lum = lum[:, np.newaxis] # (N, 1)
        # Lerp
        pixels = lum + (pixels - lum) * saturation
        pixels = np.clip(pixels, 0, 1)

    # 3. Quantization (Posterization) to reduce noise
    if quantize > 0 and not delight:
        print(f"Quantizing to {quantize} levels per channel...")
        pixels = np.round(pixels * quantize) / float(quantize)

    # Check unique again
    pixels_rounded = np.round(pixels, 5)
    unique_pixels = np.unique(pixels_rounded, axis=0)
    print(f"Unique colors after processing: {len(unique_pixels)}")
    
    if delight:
        print(f"Delighting enabled! Clustering on Chromaticity for {max_colors} materials...")
        # Compute Chromaticity (normalize by sum to remove intensity)
        # Add epsilon to avoid divide by zero for black
        sums = np.sum(pixels, axis=1, keepdims=True)
        chroma = pixels / (sums + 1e-9)
        
        # Cluster based on Chroma
        # We need to handle potential NaN or inf if sums is 0 (handled by epsilon, but strictly black is an edge case)
        
        try:
            chroma_codebook, _ = scipy.cluster.vq.kmeans(chroma, max_colors, iter=20)
        except Exception as e:
            print(f"Chroma Kmeans failed: {e}")
            chroma_codebook = chroma[:max_colors]

        # Assign pixels to chroma clusters
        indices, _ = scipy.cluster.vq.vq(chroma, chroma_codebook)
        
        # Reconstruct "Unlit" colors for the palette
        # For each cluster, pick the brightest original pixels to represent the material
        codebook = np.zeros((len(chroma_codebook), 3))
        
        for i in range(len(chroma_codebook)):
            # Get original pixels belonging to this material
            cluster_mask = (indices == i)
            if not np.any(cluster_mask):
                continue
                
            cluster_pixels = pixels[cluster_mask]
            
            # Metric for "brightness": Sum of channels or Max channel
            # We want the "lit" version, so the brightest ones.
            brightness = np.sum(cluster_pixels, axis=1)
            
            # Take top 10% brightest to avoid single outliers but get the "lit" color
            # If cluster is small, just take max or mean
            if len(cluster_pixels) > 10:
                threshold = np.percentile(brightness, 90)
                brightest = cluster_pixels[brightness >= threshold]
                representative = np.mean(brightest, axis=0)
            else:
                representative = np.mean(cluster_pixels, axis=0)
                
            codebook[i] = representative
            
        print(f"Delighted palette generated with {len(codebook)} materials.")
            
    else:
        # Standard RGB Clustering
        # Quantize to max_colors using k-means
        print(f"Quantizing {len(pixels)} voxels to {max_colors} colors...")
        
        if len(unique_pixels) <= max_colors:
            print(f"Found {len(unique_pixels)} unique colors. using exact palette.")
            codebook = unique_pixels
        else:
            # Use simple k-means with high iter
            try:
                codebook, _ = scipy.cluster.vq.kmeans(pixels, max_colors, iter=40)
            except Exception as e:
                print(f"Kmeans failed: {e}")
                indices = np.random.choice(len(pixels), max_colors, replace=False)
                codebook = pixels[indices]
            
        # Assign each voxel to a color index
        indices, _ = scipy.cluster.vq.vq(pixels, codebook)
    
    # Map (x,y,z) -> color_index (1-based)
    voxel_indices = {}
    # keys is already defined and aligned with pixels
    for i, k in enumerate(keys):
        voxel_indices[k] = indices[i] + 1
    
    # Prepare Palette Chunk (RGBA)
    palette_bytes = bytearray(1024)
    for i, color in enumerate(codebook):
        r, g, b = (np.clip(color, 0, 1) * 255).astype(int)
        idx = i * 4
        palette_bytes[idx] = r
        palette_bytes[idx+1] = g
        palette_bytes[idx+2] = b
        palette_bytes[idx+3] = 255
    
    rgba_chunk = write_chunk('RGBA', palette_bytes)

    # 2. Split into chunks (256x256x256)
    chunks = {} # (cx, cy, cz) -> list of (lx, ly, lz, color_idx)
    
    for (x, y, z), color_idx in voxel_indices.items():
        cx, lx = divmod(x, 256)
        cy, ly = divmod(y, 256)
        cz, lz = divmod(z, 256)
        
        ckey = (cx, cy, cz)
        if ckey not in chunks:
            chunks[ckey] = []
        chunks[ckey].append((lx, ly, lz, color_idx))
        
    sorted_ckeys = sorted(chunks.keys())
    num_models = len(chunks)
    print(f"Split into {num_models} chunks.")
    
    # 0. Generate PACK chunk (Required for multiple models)
    pack_payload = struct.pack('<I', num_models)
    pack_chunk = write_chunk('PACK', pack_payload)

    # 3. Generate Models (SIZE + XYZI pairs)
    # We will write them sequentially. Model ID 0 is the first one written, etc.
    
    model_chunks_data = bytearray()
    # Prepend PACK chunk
    model_chunks_data += pack_chunk
    
    for ckey in sorted_ckeys:
        voxels_in_chunk = chunks[ckey]
        
        # SIZE chunk
        # Although the bounding box might be smaller, using 256 is safe/standard for grid alignment
        size_payload = struct.pack('<III', 256, 256, 256)
        model_chunks_data += write_chunk('SIZE', size_payload)
        
        # XYZI chunk
        xyzi_payload = bytearray()
        xyzi_payload += struct.pack('<I', len(voxels_in_chunk))
        for lx, ly, lz, ci in voxels_in_chunk:
            xyzi_payload += struct.pack('<BBBB', lx, ly, lz, ci)
            
        model_chunks_data += write_chunk('XYZI', xyzi_payload)
        
def write_vox(voxel_map, filename, resolution, gamma=2.2, quantize=24, saturation=1.0, max_colors=255, delight=False):
    # 1. Extract unique colors and build palette
    unique_voxels = []
    
    # Efficiently collect all colors
    voxel_items = list(voxel_map.items())
    if not voxel_items:
        print("No voxels generated!")
        return

    # Unpack keys and values in strict order
    keys = [k for k, v in voxel_items]
    all_colors = [v for k, v in voxel_items]

    pixels = np.array(all_colors) # (N, 3) floats 0-1
    
    print(f"Sample raw colors: {pixels[:5]}")
    
    # 1. Gamma Correction
    if gamma != 1.0:
        print(f"Applying Gamma {gamma} correction...")
        pixels = np.power(np.clip(pixels, 0, 1), 1.0/gamma)

    # 2. Saturation Adjustment
    if saturation != 1.0:
        print(f"Applying Saturation {saturation}...")
        pixels = np.clip(pixels, 0, 1)

    # 3. Quantization (Posterization) to reduce noise
    if quantize > 0 and not delight:
        print(f"Quantizing to {quantize} levels per channel...")
        pixels = np.round(pixels * quantize) / float(quantize)

    # Check unique again
    pixels_rounded = np.round(pixels, 5)
    unique_pixels = np.unique(pixels_rounded, axis=0)
    print(f"Unique colors after processing: {len(unique_pixels)}")
    
    if delight:
        print(f"Delighting enabled! Clustering on Chromaticity for {max_colors} materials...")
        sums = np.sum(pixels, axis=1, keepdims=True)
        chroma = pixels / (sums + 1e-9)
        
        try:
            chroma_codebook, _ = scipy.cluster.vq.kmeans(chroma, max_colors, iter=20)
        except Exception as e:
            print(f"Chroma Kmeans failed: {e}")
            chroma_codebook = chroma[:max_colors]

        indices, _ = scipy.cluster.vq.vq(chroma, chroma_codebook)
        codebook = np.zeros((len(chroma_codebook), 3))
        
        for i in range(len(chroma_codebook)):
            cluster_mask = (indices == i)
            if not np.any(cluster_mask): continue
            cluster_pixels = pixels[cluster_mask]
            brightness = np.sum(cluster_pixels, axis=1)
            if len(cluster_pixels) > 10:
                threshold = np.percentile(brightness, 90)
                brightest = cluster_pixels[brightness >= threshold]
                representative = np.mean(brightest, axis=0)
            else:
                representative = np.mean(cluster_pixels, axis=0)
            codebook[i] = representative
            
        print(f"Delighted palette generated with {len(codebook)} materials.")
            
    else:
        print(f"Quantizing {len(pixels)} voxels to {max_colors} colors...")
        if len(unique_pixels) <= max_colors:
            codebook = unique_pixels
        else:
            try:
                codebook, _ = scipy.cluster.vq.kmeans(pixels, max_colors, iter=40)
            except Exception as e:
                print(f"Kmeans failed: {e}")
                indices = np.random.choice(len(pixels), max_colors, replace=False)
                codebook = pixels[indices]
        indices, _ = scipy.cluster.vq.vq(pixels, codebook)
    
    voxel_indices = {}
    for i, k in enumerate(keys):
        voxel_indices[k] = indices[i] + 1
    
    # Prepare Palette Chunk (RGBA)
    palette_bytes = bytearray(1024)
    for i, color in enumerate(codebook):
        r, g, b = (np.clip(color, 0, 1) * 255).astype(int)
        idx = i * 4
        palette_bytes[idx] = r
        palette_bytes[idx+1] = g
        palette_bytes[idx+2] = b
        palette_bytes[idx+3] = 255
    rgba_chunk = write_chunk('RGBA', palette_bytes)

    # 2. Split into chunks
    chunks = {} 
    for (x, y, z), color_idx in voxel_indices.items():
        cx, lx = divmod(x, 256)
        cy, ly = divmod(y, 256)
        cz, lz = divmod(z, 256)
        ckey = (cx, cy, cz)
        if ckey not in chunks: chunks[ckey] = []
        chunks[ckey].append((lx, ly, lz, color_idx))
        
    sorted_ckeys = sorted(chunks.keys())
    num_models = len(chunks)
    print(f"Split into {num_models} chunks.")
    
    pack_payload = struct.pack('<I', num_models)
    pack_chunk = write_chunk('PACK', pack_payload)

    # 3. Generate Models
    model_chunks_data = bytearray()
    model_chunks_data += pack_chunk
    
    for ckey in sorted_ckeys:
        voxels_in_chunk = chunks[ckey]
        size_payload = struct.pack('<III', 256, 256, 256)
        model_chunks_data += write_chunk('SIZE', size_payload)
        xyzi_payload = bytearray()
        xyzi_payload += struct.pack('<I', len(voxels_in_chunk))
        for lx, ly, lz, ci in voxels_in_chunk:
            xyzi_payload += struct.pack('<BBBB', lx, ly, lz, ci)
        model_chunks_data += write_chunk('XYZI', xyzi_payload)
        
    # 4. Generate Scene Graph
    # Hierarchy:
    # 0: nTRN (World) -> Child 1
    # 1: nGRP (Group) -> Children [2, 4, 6...]
    # 2: nTRN (Chunk 0) -> Child 3
    # 3: nSHP (Chunk 0) -> Model 0
    # ...
    
    world_trn_id = 0
    group_id = 1
    next_id = 2
    
    chunk_trn_ids = []
    graph_data = bytearray()
    
    for i, ckey in enumerate(sorted_ckeys):
        cx, cy, cz = ckey
        model_id = i
        
        trn_id = next_id
        shp_id = next_id + 1
        next_id += 2
        
        chunk_trn_ids.append(trn_id)
        
        # Chunk nTRN
        tx, ty, tz = int(cx * 256), int(cy * 256), int(cz * 256)
        frames = []
        frame = {}
        if tx != 0 or ty != 0 or tz != 0:
            frame['_t'] = f"{tx} {ty} {tz}"
        # frame['_r'] = "4" # Optional: Identity rotation
        frames.append(frame)
        
        trn_payload = struct.pack('<I', trn_id)
        trn_payload += write_dict({'_name': f'chunk_{i}'})
        trn_payload += struct.pack('<I', shp_id)
        trn_payload += struct.pack('<i', -1) # reserved
        trn_payload += struct.pack('<i', 0) # layer 0
        trn_payload += struct.pack('<I', 1) # num frames
        trn_payload += write_dict(frames[0])
        graph_data += write_chunk('nTRN', trn_payload)
        
        # Chunk nSHP
        shp_payload = struct.pack('<I', shp_id)
        shp_payload += write_dict({})
        shp_payload += struct.pack('<I', 1) # num models
        shp_payload += struct.pack('<I', model_id)
        shp_payload += write_dict({})
        graph_data += write_chunk('nSHP', shp_payload)
        
    # Group nGRP
    grp_payload = struct.pack('<I', group_id)
    grp_payload += write_dict({})
    grp_payload += struct.pack('<I', len(chunk_trn_ids))
    for tid in chunk_trn_ids:
        grp_payload += struct.pack('<I', tid)
    
    # World nTRN
    world_frames = [{}] # Identity
    world_payload = struct.pack('<I', world_trn_id)
    world_payload += write_dict({'_name': 'world'})
    world_payload += struct.pack('<I', group_id)
    world_payload += struct.pack('<i', -1)
    world_payload += struct.pack('<i', 0)
    world_payload += struct.pack('<I', 1)
    world_payload += write_dict(world_frames[0])
    
    # Final Graph Order: World TRN, Group, Children...
    final_graph_data = write_chunk('nTRN', world_payload) + write_chunk('nGRP', grp_payload) + graph_data
    
    # LAYR Chunk
    layr_payload = struct.pack('<I', 0)
    layr_payload += write_dict({'_name': 'base'})
    layr_payload += struct.pack('<i', -1)
    final_graph_data = write_chunk('LAYR', layr_payload) + final_graph_data

    # Construct MAIN
    with open(filename, 'wb') as f:
        f.write(b'VOX ')
        f.write(struct.pack('<I', 150))
        
        main_children = model_chunks_data + rgba_chunk + final_graph_data
        
        f.write(b'MAIN')
        f.write(struct.pack('<II', 0, len(main_children)))
        f.write(main_children)
        
    print(f"Written {len(keys)} voxels to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Convert OBJ with vertex colors to VOX.')
    parser.add_argument('input', help='Input OBJ file')
    parser.add_argument('output', help='Output VOX file')
    parser.add_argument('resolution', type=int, default=128, help='Target resolution (grid size)')
    parser.add_argument('--gamma', type=float, default=2.2, help='Gamma correction factor (default 2.2)')
    parser.add_argument('--quantize', type=int, default=24, help='Color quantization levels per channel (default 24)')
    parser.add_argument('--saturation', type=float, default=1.0, help='Saturation multiplier (default 1.0)')
    parser.add_argument('--palette-colors', type=int, default=255, help='Max colors in palette (default 255)')
    parser.add_argument('--vertical-stretch', type=float, default=1.0, help='Vertical stretch factor (Z-axis scaling)')
    parser.add_argument('--delight', action='store_true', help='Remove lighting by clustering on chromaticity and picking brightest colors')
    
    args = parser.parse_args()
    
    print(f"Loading {args.input}...")
    verts, colors, faces = load_obj(args.input)
    print(f"Loaded {len(verts)} vertices, {len(faces)} faces.")
    
    if args.vertical_stretch != 1.0:
        print(f"Applying vertical stretch: {args.vertical_stretch}")
        # Scale Z axis (index 2 after the swap in load_obj)
        verts[:, 2] *= args.vertical_stretch
    
    if len(faces) == 0:
        print("No faces found. Treating as point cloud? (Not implemented)")
        sys.exit(1)
        
    voxels = get_voxel_grid(verts, colors, faces, args.resolution)
    
    write_vox(voxels, args.output, args.resolution, args.gamma, args.quantize, args.saturation, args.palette_colors, args.delight)

if __name__ == "__main__":
    main()
