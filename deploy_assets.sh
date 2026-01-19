#!/bin/bash

# Configuration
SOURCE_DIR="."
ASSET_DIR="csg_assets"
GAME_ASSET_DIR="$HOME/love_exp/assets/csg_assets"

# Ensure directories exist
mkdir -p "$ASSET_DIR"
mkdir -p "$GAME_ASSET_DIR"

echo "Deploying assets..."

SKIP_RECOMPILE=false
if [[ "$1" == "--no-recompile" ]]; then
    SKIP_RECOMPILE=true
    echo "Skipping recompile step as requested."
fi

# 1. Convert any .vox in vox/ to .gltf (if newer than target)
if [ "$SKIP_RECOMPILE" = false ]; then
    for vox_path in vox/*.vox; do
        # Skip if no vox files
        [ -e "$vox_path" ] || continue
        
        vox_file=$(basename "$vox_path")
        base_name=$(basename "$vox_file" .vox)
        gltf_file="$ASSET_DIR/$base_name.gltf"
        
        # Check if recompile is needed (vox newer than gltf)
        if [ ! -f "$gltf_file" ] || [ "$vox_path" -nt "$gltf_file" ]; then
            echo "Processing $vox_path (needs update)..."
            # Run converter with --no-center to respect manual origins
            python3 vox_to_gltf.py --no-center "$vox_path"
            
            # Move to assets dir from the location where vox_to_gltf generated them
            # vox_to_gltf.py outputs to the same dir as the input .vox
            mv "vox/${base_name}.gltf" "$ASSET_DIR/" 2>/dev/null
            mv "vox/${base_name}.bin" "$ASSET_DIR/" 2>/dev/null
            mv "palette_texture.png" "$ASSET_DIR/" 2>/dev/null
        else
            echo "Skipping $vox_path (already up to date)."
        fi
    done
fi

# Ensure palette_texture.png is always in ASSET_DIR even if we skipped recompile
if [ ! -f "$ASSET_DIR/palette_texture.png" ] && [ -f "palette_texture.png" ]; then
    mv "palette_texture.png" "$ASSET_DIR/"
fi

# 2. Copy all assets to game directory
echo "Copying to game directory: $GAME_ASSET_DIR"
cp -rv "$ASSET_DIR"/* "$GAME_ASSET_DIR/"

echo "Done."
