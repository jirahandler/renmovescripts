#!/bin/bash

# Function to rename files with specific suffixes to standard extensions
rename_files() {
    for file in "$1"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, call the function recursively
            rename_files "$file"
        elif [ -f "$file" ]; then
            # If it's a file, rename it if it ends with the specific suffixes
            filename=$(basename -- "$file")
            directory=$(dirname -- "$file")

            if [[ "$filename" == *_pdf\' ]]; then
                newfilename="${filename%_pdf\'}_pdf.pdf"
                echo "Renaming: $file to $directory/$newfilename"
                mv "$file" "$directory/$newfilename"
            else
                for ext in idx gpg dat html desktop JPG db xsd keys ilg config csmo tsv pa odt init rev json tif nav fff page pem md crt p12 key ind conf log sshfs dwl bak dtx menu CSV bmp so com xlsm mp4 svg rsa c kbx inf toc PDF glo ipynb dwg hosts nb glade ico f95 m eps cer ods xls ins gif f90 map vcf ID xml pdf wav aux pdf-new pkpass csr snm ist out dwl2 revoke structure Store directory WEEK mat ppm f zip; do
                    if [[ "$filename" == *_$ext ]]; then
                        newfilename="${filename%_$ext}.$ext"
                        echo "Renaming: $file to $directory/$newfilename"
                        mv "$file" "$directory/$newfilename"
                        break
                    fi
                done
            fi
        fi
    done
}

# Start the renaming process from the current directory
rename_files "."

echo "Renaming process completed."
