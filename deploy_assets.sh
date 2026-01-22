#!/bin/bash

# Colors for UI
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Config
ASSET_DIR="csg_assets"
GAME_ASSET_DIR="$HOME/love_exp/assets/csg_assets"

# Stats
built=0
skipped=0
failed=0
collections=0

# Ensure directories exist
mkdir -p "$ASSET_DIR"
mkdir -p "$GAME_ASSET_DIR"

clear
echo -e "${BOLD}--- CSG ASSET FORGE & PUBLISHER ---${NC}\n"

# 1. Forge Stage (JSON -> GLTF)
echo -e "${BLUE}🔨 FORGING ASSETS${NC}"
for json_path in csg/*.json; do
    [ -e "$json_path" ] || continue
    asset_name=$(basename "$json_path" .json)
    
    # Check if it is a collection or registry (non-forgable)
    if grep -qE '"layout":|"type": "collection"' "$json_path" || [[ "$asset_name" == *"registry"* ]]; then
        # Handle as collection later
        continue
    fi

    # Check if we should skip
    status=$(python3 tools/check_hash.py "$asset_name" 2>/dev/null)
    
    if [ "$status" == "update" ]; then
        echo -en "  - ${BOLD}$asset_name${NC} ... "
        python3 csg_compiler.py "$json_path" > /dev/null 2> /tmp/csg_err.log
        if [ $? -eq 0 ]; then
            python3 vox_to_gltf.py --no-center "vox/$asset_name.vox" > /dev/null 2>> /tmp/csg_err.log
            if [ $? -eq 0 ]; then
                mv "vox/${asset_name}.gltf" "$ASSET_DIR/" 2>/dev/null
                mv "vox/${asset_name}.bin" "$ASSET_DIR/" 2>/dev/null
                echo -e "${GREEN}BUILT${NC}"
                ((built++))
            else
                echo -e "${RED}GLTF FAIL${NC}"
                ((failed++))
            fi
        else
            echo -e "${RED}CSG FAIL${NC}"
            ((failed++))
        fi
    else
        ((skipped++))
    fi
done

# 2. Collection Stage (Publishing logic assets)
echo -e "\n${BLUE}📚 PUBLISHING COLLECTIONS${NC}"
for json_path in csg/*.json; do
    [ -e "$json_path" ] || continue
    asset_name=$(basename "$json_path" .json)
    
    if grep -qE '"layout":|"type": "collection"' "$json_path" || [[ "$asset_name" == *"registry"* ]]; then
        # Only copy if changed or missing in target
        cp "$json_path" "$ASSET_DIR/"
        echo -e "  - ${BOLD}$asset_name${NC} ... ${GREEN}SYNCED${NC}"
        ((collections++))
    fi
done

# Ensure palette_texture.png is in place
if [ -f "palette_texture.png" ]; then
    mv "palette_texture.png" "$ASSET_DIR/" 2>/dev/null
fi

# 3. Registry Refresh
echo -e "\n${BLUE}📝 REFRESHING REGISTRIES${NC}"
python3 tools/tile_registry.py > /dev/null && echo -e "  - ${GREEN}Tile Registry Updated${NC}"
python3 tools/asset_registry.py > /dev/null && echo -e "  - ${GREEN}Asset Registry Updated${NC}"

# 4. Publish Stage (Sync to Engine)
echo -e "\n${BLUE}🚀 PUBLISHING TO ENGINE${NC}"
echo -en "  - Syncing to $GAME_ASSET_DIR ... "
# Using rsync for efficient incremental updates and --delete to remove stale files
rsync -av --delete --exclude ".*" "$ASSET_DIR/" "$GAME_ASSET_DIR/" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SUCCESS${NC}"
else
    echo -e "${RED}SYNC FAILED${NC}"
fi

# 5. Tile Compilation (Resolving anchors/lights)
# This MUST happen after sync so we don't overwrite compiled files with sources
echo -e "\n${BLUE}🧩 COMPILING TILES (Post-Sync)${NC}"
python3 tile_compiler.py | while read -r line; do
    fname=$(echo "$line" | awk '{print $2}')
    echo -e "  - ${BOLD}$fname${NC} ... ${GREEN}COMPILED${NC}"
done

# Final Summary
echo -e "\n${BOLD}=== PUBLISH SUMMARY ===${NC}"
echo -e "  Forged:      ${GREEN}$built${NC}"
echo -e "  Collections: ${BLUE}$collections${NC}"
echo -e "  Skipped:     ${YELLOW}$skipped${NC}"
if [ $failed -gt 0 ]; then
    echo -e "  Failed:      ${RED}$failed${NC}"
fi
echo -e "  Target:      ${BLUE}$GAME_ASSET_DIR${NC}"
echo -e "\n${BOLD}READY FOR ENGINE RELOAD!${NC}"