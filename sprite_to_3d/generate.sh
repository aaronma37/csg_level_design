#!/bin/bash
set -e

# 1. Generate Voxel Model from Blueprint
echo "Step 1: Generating Voxel Model..."
python3 sprite_to_3d/generator.py

# 1.5 Ground the model
echo "Step 1.5: Grounding Model..."
python3 sprite_to_3d/move_to_ground.py sprite_to_3d/vox_construction/hero_model.vox sprite_to_3d/vox_construction/hero_model.vox

# 2. Decompose and Rig the Model
echo "Step 2: Rigging and Decomposing..."
python3 sprite_to_3d/rigger.py

# 3. Create Modular GLTF Assets
echo "Step 3: Creating GLTF Assets..."
python3 sprite_to_3d/create_modular_assets.py \
    sprite_to_3d/actor_assets/hero/rig.json \
    sprite_to_3d/actor_assets/hero/ \
    base

# 4. Deploy to Preview v2
echo "Step 4: Deploying to Preview v2..."
mkdir -p sprite_to_3d/preview_v2/assets
cp sprite_to_3d/actor_assets/hero/*.gltf sprite_to_3d/preview_v2/assets/
cp sprite_to_3d/actor_assets/hero/*.bin sprite_to_3d/preview_v2/assets/
cp sprite_to_3d/actor_assets/hero/*.png sprite_to_3d/preview_v2/assets/
# Copy the rig.json as well if needed
cp sprite_to_3d/actor_assets/hero/rig.json sprite_to_3d/preview_v2/assets/

echo "Generation and Deployment Complete!"

