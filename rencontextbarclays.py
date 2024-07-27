import os
import pdfplumber
import re
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
    return text

def rename_bank_statements(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            text = extract_text_from_pdf(file_path)

            bank_name = "Barclays"
            account_number = "0000"
            statement_date = extract_statement_date(text)

            new_filename = f"{bank_name}_Statement_{account_number}_{statement_date}.pdf"
            new_file_path = os.path.join(directory, new_filename)

            # Check if the new filename already exists to avoid overwriting
            if not os.path.exists(new_file_path):
                os.rename(file_path, new_file_path)
                print(f"Renamed '{filename}' to '{new_filename}'")
            else:
                print(f"Skipping renaming of '{filename}' as '{new_filename}' already exists")

def extract_statement_date(text):
    # Regular expression to extract dates from the statement period string
    match = re.search(r"Statement Period\s(\d{2}/\d{2}/\d{2})\s-\s(\d{2}/\d{2}/\d{2})", text)
    if match:
        start_date = datetime.strptime(match.group(1), "%m/%d/%y")
        end_date = datetime.strptime(match.group(2), "%m/%d/%y")
        # Use end date as the statement date for the filename
        return end_date.strftime("%Y-%m-%d")
    else:
        return "UnknownDate"

# Replace 'your_directory_path' with the path to the directory containing your bank statements
rename_bank_statements('.')
