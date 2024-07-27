#!/bin/bash

# Define the hardcoded temporary directory
TEMP_DIR="$HOME/tmp"

# Function to normalize the PDF filename
normalize_filename() {
  local filename="$1"
  local dir
  local base
  local ext
  dir=$(dirname "$filename")
  base=$(basename "$filename" .pdf)
  base=${base//[()]/_}   # Replace brackets with underscores
  base=${base//,/}       # Remove commas
  base=${base//[^[:alnum:]_]/_}  # Replace non-alphanumeric characters (except underscore) with underscores
  echo "$dir/$base.pdf"
}

# Function to clean a PDF
clean_pdf() {
  local input_file="$1"
  local cleaned_file="${input_file%.pdf}_cleaned.pdf"

  gs -o "$cleaned_file" -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress "$input_file" 2>> "errors.log"

  if [[ $? -eq 0 ]]; then
    mv "$cleaned_file" "$input_file"
  else
    rm -f "$cleaned_file"
    echo "$input_file" >> "failed_files.txt"
  fi
}

# Function to compress a PDF by rasterizing it
compress_pdf() {
  local input_file="$1"
  local normalized_file
  normalized_file=$(normalize_filename "$input_file")
  local output_file="temp_${normalized_file##*/}"

  if [[ "$input_file" != "$normalized_file" ]]; then
    mv "$input_file" "$normalized_file"
    input_file="$normalized_file"
  fi

  echo "Processing file: $input_file"

  # Clean the PDF to handle structural issues
  clean_pdf "$input_file"

  # Convert PDF to images and back to PDF using magick
  magick -density 150 "$input_file" -quality 50 "$output_file"

  if [[ $? -eq 0 ]]; then
    original_size=$(stat -f%z "$input_file")
    new_size=$(stat -f%z "$output_file")

    if [[ $new_size -lt $original_size ]]; then
      mv "$output_file" "$input_file"
      echo "$input_file -> ${new_size} bytes (reduced from ${original_size} bytes)" >> "changed_files.txt"
    else
      echo "$input_file -> ${new_size} bytes (no reduction)" >> "unchanged_files.txt"
      rm -f "$output_file"
    fi
  else
    rm -f "$output_file"
    echo "$input_file" >> "failed_files.txt"
  fi

  # Cleanup temporary files after processing each file
  delete_temp_files
}

export -f normalize_filename
export -f clean_pdf
export -f compress_pdf

# Function to delete temporary files safely
delete_temp_files() {
  if [[ -d "$TEMP_DIR" && "$TEMP_DIR" != "/" && "$TEMP_DIR" != "" ]]; then
    rm -rf "$TEMP_DIR"/*
  else
    echo "Temporary directory is not set or is invalid. Skipping cleanup."
  fi
}

# Function to handle cleanup on exit
cleanup() {
  echo "Cleaning up..."
  delete_temp_files
  echo "Done."
}

# Trap to handle script exit
trap 'cleanup; exit' INT TERM EXIT

# Main function to compress PDFs in the specified folder
compress_pdfs_in_folder() {
  local folder_path="$1"
  delete_temp_files

  > "failed_files.txt"
  > "errors.log"
  > "unchanged_files.txt"
  > "processed_files.txt"

  # Ensure changed_files.txt exists
  touch "changed_files.txt"

  # Recursively find all PDF files in the specified folder
  find "$folder_path" -type f -name "*.pdf" > "pdf_files.txt"

  # Exclude already processed files
  grep -v -F -f "changed_files.txt" "pdf_files.txt" > "remaining_files.txt"

  # Process each PDF file
  while IFS= read -r file; do
    compress_pdf "$file"
  done < "remaining_files.txt"

  cat "remaining_files.txt" >> "processed_files.txt"
}

if [[ -z "$1" ]]; then
  echo "Usage: $0 <folder_path>"
  exit 1
fi

folder_path="$1"
compress_pdfs_in_folder "$folder_path"
