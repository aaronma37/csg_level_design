#!/bin/bash

# Define directories
SOURCE_DIR="$(dirname "$0")/actor_assets"
TARGET_DIR="$HOME/love_exp/assets/actor_assets"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy files
echo "Deploying actor assets from '$SOURCE_DIR' to '$TARGET_DIR'..."
cp -r "$SOURCE_DIR"/* "$TARGET_DIR"/

if [ $? -eq 0 ]; then
    echo "Deployment successful."
else
    echo "Deployment failed."
    exit 1
fi
