#!/bin/bash

# Script to delete folders from a list if they exist in the data directory recursively.

# Input file containing folder names (one per line)
FOLDER_LIST="folders_to_delete.txt"

# Base directory where we search for folders
BASE_DIR="./data"

# Check if the folder list file exists
if [[ ! -f "$FOLDER_LIST" ]]; then
    echo "Error: File $FOLDER_LIST not found!"
    exit 1
fi

# Iterate over each folder name in the list
while IFS= read -r FOLDER_NAME; do
    echo "Searching for folder: $FOLDER_NAME"
    
    # Find folders matching the name under the base directory
    FOUND_FOLDERS=$(find "$BASE_DIR" -type d -name "$FOLDER_NAME")
    
    # Check if any folders were found
    if [[ -z "$FOUND_FOLDERS" ]]; then
        echo "Folder $FOLDER_NAME not found. Skipping..."
    else
        # Remove each folder found
        for FOLDER in $FOUND_FOLDERS; do
            echo "Removing folder: $FOLDER"
            rm -rf "$FOLDER"
        done
    fi
done < "$FOLDER_LIST"

echo "Folder removal process completed."
