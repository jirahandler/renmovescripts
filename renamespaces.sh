#!/bin/bash

# Function to rename directories and files
rename_items() {
    find "$1" -depth -name "* *" | while read -r item; do
        # Get the item name and parent directory
        itemname=$(basename -- "$item")
        parentdir=$(dirname -- "$item")
        
        # Replace spaces with underscores
        newname=$(echo "$itemname" | tr ' ' '_')
        
        # Rename the item if needed
        if [ "$itemname" != "$newname" ]; then
            mv "$item" "$parentdir/$newname"
        fi
    done
}

# Start the renaming process from the current directory
rename_items "."

echo "Renaming process completed."
