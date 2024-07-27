import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import io


# Function to check if the page size is A4 or letter
def is_a4_or_letter(page_size):
    return page_size == letter or page_size == A4


# Function to compress the PDF
def compress_pdf(input_file, temp_file):
    pdf_writer = PdfFileWriter()
    try:
        pdf_reader = PdfFileReader(input_file, strict=False)
    except Exception as e:
        raise Exception(f"Could not read PDF {input_file}: {e}")

    for page_num in range(pdf_reader.getNumPages()):
        try:
            page = pdf_reader.getPage(page_num)
        except Exception as e:
            raise Exception(f"Could not get page {page_num} from {input_file}: {e}")

        page_size = page.mediaBox.upperRight

        if is_a4_or_letter(page_size):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=page_size)
            can.setPageCompression(1)
            # Adjust the DPI
            can.scale(0.5, 0.5)  # assuming the original DPI is 300
            can.drawString(100, 100, "Compressed")
            can.save()

            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            try:
                page.mergePage(new_pdf.getPage(0))
            except Exception as e:
                raise Exception(f"Could not merge page for {input_file}: {e}")

        pdf_writer.addPage(page)

    with open(temp_file, "wb") as out_file:
        pdf_writer.write(out_file)


# Function to compress PDFs in a folder if they are larger than 1MB and record changes
def compress_pdfs_in_folder(folder_path):
    changed_files = []
    failed_files = []

    # Load processed files from previous runs
    processed_files = set()
    processed_files_path = os.path.join(folder_path, "processed_files.txt")
    if os.path.exists(processed_files_path):
        with open(processed_files_path, "r") as f:
            processed_files = set(f.read().splitlines())

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                input_file = os.path.join(root, file)
                if (
                    os.path.getsize(input_file) > 1 * 1024 * 1024
                    and input_file not in processed_files
                ):  # Check if file is larger than 1MB
                    temp_file = os.path.join(root, f"temp_{file}")
                    try:
                        compress_pdf(input_file, temp_file)
                        os.replace(temp_file, input_file)
                        changed_files.append((input_file, os.path.getsize(input_file)))
                        processed_files.add(input_file)
                        print(f"Compressed {input_file}")
                    except Exception as e:
                        print(f"Failed to compress {input_file}: {e}")
                        failed_files.append(input_file)
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

    # Save the list of changed files and their sizes
    with open(os.path.join(folder_path, "changed_files.txt"), "w") as f:
        for original_file, new_size in changed_files:
            f.write(f"{original_file} -> {new_size} bytes\n")

    # Save the list of processed files
    with open(processed_files_path, "w") as f:
        for processed_file in processed_files:
            f.write(f"{processed_file}\n")

    # Save the list of failed files
    with open(os.path.join(folder_path, "failed_files.txt"), "w") as f:
        for failed_file in failed_files:
            f.write(f"{failed_file}\n")


if __name__ == "__main__":
    folder_path = "./"
    compress_pdfs_in_folder(folder_path)
