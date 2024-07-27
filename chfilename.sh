#!/bin/bash

# Function to replace unwanted characters in filenames with underscores
sanitize_filename() {
    filename="$1"
    directory="$2"

    # Extract the name and extension
    name="${filename%.*}"
    extension="${filename##*.}"

    # Replace characters in the name
    sanitized_name=$(echo "$name" | tr ' .,[]{}()' '_')

    # Construct the new filename
    if [ "$extension" != "$filename" ]; then
        newfilename="${sanitized_name}.${extension}"
    else
        newfilename="$sanitized_name"
    fi

    echo "$directory/$newfilename"
}

# Function to recursively rename files
rename_files() {
    for file in "$1"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, call the function recursively
            rename_files "$file"
        elif [ -f "$file" ]; then
            # If it's a file, rename it
            filename=$(basename -- "$file")
            directory=$(dirname -- "$file")
            
            newfilepath=$(sanitize_filename "$filename" "$directory")
            
            # Rename the file if the name has changed
            if [ "$file" != "$newfilepath" ]; then
                mv "$file" "$newfilepath"
            fi
        fi
    done
}

# Start the renaming process from the current directory
rename_files "./"

echo "Renaming process completed."
