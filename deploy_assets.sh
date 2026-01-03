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

# 1. Convert any .vox in root to .gltf (if newer than target)
if [ "$SKIP_RECOMPILE" = false ]; then
    for vox_file in *.vox; do
        # Skip if no vox files
        [ -e "$vox_file" ] || continue
        
        base_name=$(basename "$vox_file" .vox)
        gltf_file="$ASSET_DIR/$base_name.gltf"
        
        # Check if recompile is needed (vox newer than gltf)
        if [ ! -f "$gltf_file" ] || [ "$vox_file" -nt "$gltf_file" ]; then
            echo "Processing $vox_file (needs update)..."
            # Run converter
            ./venv/bin/python vox_to_gltf.py "$vox_file"
            
            # Move to assets dir
            mv "${base_name}.gltf" "$ASSET_DIR/" 2>/dev/null
            mv "${base_name}.bin" "$ASSET_DIR/" 2>/dev/null
            mv "palette_texture.png" "$ASSET_DIR/" 2>/dev/null
        else
            echo "Skipping $vox_file (already up to date)."
        fi
    done
fi

# Ensure palette_texture.png is always in ASSET_DIR even if we skipped recompile
if [ ! -f "$ASSET_DIR/palette_texture.png" ] && [ -f "palette_texture.png" ]; then
    mv "palette_texture.png" "$ASSET_DIR/"
fi

# 2. Copy all assets to game directory
echo "Copying to game directory: $GAME_ASSET_DIR"
cp -v "$ASSET_DIR"/* "$GAME_ASSET_DIR/"

echo "Done."
