import os
import re
from PyPDF2 import PdfFileReader

def extract_info_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfFileReader(file)
        first_page = reader.getPage(0)
        text = first_page.extract_text()

        # Extract the date
        date_pattern = re.compile(r'New balance as of (\d{2}/\d{2}/\d{2})')
        date_match = date_pattern.search(text)
        if date_match:
            date = date_match.group(1)
            # Convert MM/DD/YY to DDMMYY
            date_parts = date.split('/')
            formatted_date = date_parts[1] + date_parts[0] + date_parts[2]
        else:
            formatted_date = None

        # Extract the account number
        account_pattern = re.compile(r'Account number ending in: (\d{4})')
        account_match = account_pattern.search(text)
        if account_match:
            account_number = account_match.group(1)
        else:
            account_number = None

        return formatted_date, account_number

def rename_files_in_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith('.pdf'):
                file_path = os.path.join(root, filename)
                formatted_date, account_number = extract_info_from_pdf(file_path)
                if formatted_date and account_number:
                    new_filename = f"Statement_{formatted_date}_{account_number}.pdf"
                    new_file_path = os.path.join(root, new_filename)
                    
                    # Check if the file already exists and remove it
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    
                    os.rename(file_path, new_file_path)
                    print(f"Renamed {file_path} to {new_file_path}")

# Specify the directory containing the PDF files
directory_path = '.'
rename_files_in_directory(directory_path)
