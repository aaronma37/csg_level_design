#!/bin/bash
# Optimized build and deploy script

ASSET_NAME=$1
GAME_DIR="$HOME/love_exp/assets/csg_assets"

echo "=== Fast Voxel Pipeline ==="

# 1. Target specific asset if provided
if [ ! -z "$ASSET_NAME" ]; then
    # Run Generator
    GEN_SCRIPT="generators/generate_${ASSET_NAME}.py"
    if [ -f "$GEN_SCRIPT" ]; then
        echo "Generating: $ASSET_NAME"
        python3 "$GEN_SCRIPT"
    fi

    # Compile JSON to VOX
    if [ -f "csg/${ASSET_NAME}.json" ]; then
        echo "Compiling: $ASSET_NAME"
        python3 csg_compiler.py "csg/${ASSET_NAME}.json"
    fi

    # Export VOX to GLTF
    if [ -f "vox/${ASSET_NAME}.vox" ]; then
        echo "Exporting: $ASSET_NAME"
        python3 vox_to_gltf.py "vox/${ASSET_NAME}.vox" "csg/${ASSET_NAME}.gltf"
    fi
    
    # Selective Deploy
    cp "csg/${ASSET_NAME}.gltf" "csg/${ASSET_NAME}.bin" "$GAME_DIR/" 2>/dev/null
else
    echo "No asset name provided. Skipping geometry rebuilds."
fi

# 2. Always generate palette once
python3 -c "import vox_to_gltf; vox_to_gltf.generate_palette_png('csg/palette_texture.png')"
cp "csg/palette_texture.png" "$GAME_DIR/"

# 3. Always Sync Tiles and Scenes (Small files, very fast)
echo "Syncing Tiles & Scenes..."
mkdir -p "$GAME_DIR/tiles"
mkdir -p "$GAME_DIR/scenes"
cp -u csg_assets/tiles/*.lua "$GAME_DIR/tiles/"
cp -u csg_assets/scenes/*.lua "$GAME_DIR/scenes/"

echo "Done."