#!/bin/bash

# Configuration
SOURCE_DIR="."
ASSET_DIR="csg_assets"
GAME_ASSET_DIR="$HOME/love_exp/assets/csg_assets"

# Ensure directories exist
mkdir -p "$ASSET_DIR"
mkdir -p "$GAME_ASSET_DIR"

echo "=== Pre-Flight Validation ==="
python3 tools/validate_assets.py || { echo "Validation failed! Aborting deploy."; exit 1; }

echo "=== Deploying Assets ==="

# 1. Compile modified CSG to GLTF via Hashing
# Iterate all JSON files in csg/
for json_path in csg/*.json; do
    [ -e "$json_path" ] || continue
    
    asset_name=$(basename "$json_path" .json)
    
    # Check if we should skip
    status=$(python3 tools/check_hash.py "$asset_name")
    
    if [ "$status" == "update" ]; then
        echo "Recompiling $asset_name..."
        python3 csg_compiler.py "$json_path" > /dev/null
        python3 vox_to_gltf.py --no-center "vox/$asset_name.vox" > /dev/null
        
        # Move outputs
        mv "vox/${asset_name}.gltf" "$ASSET_DIR/" 2>/dev/null
        mv "vox/${asset_name}.bin" "$ASSET_DIR/" 2>/dev/null
        mv "palette_texture.png" "$ASSET_DIR/" 2>/dev/null
    else
        echo "Skipping $asset_name (cached)."
    fi
done

# Ensure palette_texture.png is in place
if [ -f "palette_texture.png" ]; then
    mv "palette_texture.png" "$ASSET_DIR/" 2>/dev/null
fi

# 2. Sync to game directory
echo "Syncing to $GAME_ASSET_DIR..."
cp -rv "$ASSET_DIR"/* "$GAME_ASSET_DIR/" > /dev/null

# 3. Build Registries
echo "Building Registries..."
python3 tools/tile_registry.py > /dev/null
python3 tools/asset_registry.py > /dev/null

# 4. Compile Tiles (Resolving anchors)
echo "Compiling Tile Definitions..."
python3 tile_compiler.py > /dev/null

# 5. Visualizer check for main test
lua visualize_scene.lua csg_assets/scenes/tactical_test_32.lua > /dev/null

echo "=== Deployment Complete ==="