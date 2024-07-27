import os
import asyncio
import aiofiles
import aiofiles.os
from concurrent.futures import ThreadPoolExecutor

# Asynchronous function to compress PDF using Ghostscript
async def compress_pdf(input_file, output_file):
    process = await asyncio.create_subprocess_exec(
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.7',
        '-dPDFSETTINGS=/ebook',  # Change this to /screen, /printer, /prepress, or /default as needed
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        '-dColorImageResolution=150',
        '-dGrayImageResolution=150',
        '-dMonoImageResolution=150',
        f'-sOutputFile={output_file}',
        input_file,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    if process.returncode != 0:
        raise Exception(f"Ghostscript error with file: {input_file}")

# Asynchronous function to process a single PDF file
async def process_file(file_info):
    input_file, root, processed_files = file_info
    print(f"Currently handling: {input_file}")
    temp_file = os.path.join(root, f"temp_{os.path.basename(input_file)}")
    try:
        await compress_pdf(input_file, temp_file)
        await aiofiles.os.replace(temp_file, input_file)
        processed_files.add(input_file)
        return input_file, os.path.getsize(input_file), None
    except Exception as e:
        if os.path.exists(temp_file):
            await aiofiles.os.remove(temp_file)
        return input_file, None, str(e)

# Asynchronous function to delete temporary files
async def delete_temp_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.startswith('temp_'):
                await aiofiles.os.remove(os.path.join(root, file))

# Function to run process_file within ThreadPoolExecutor
def sync_process_file(file_info):
    return asyncio.run(process_file(file_info))

# Asynchronous function to compress PDFs in a folder if they are larger than 1MB and record changes
async def compress_pdfs_in_folder(folder_path, max_workers=2):
    await delete_temp_files(folder_path)

    changed_files = []
    failed_files = []
    processed_files = set()

    # Load processed files from previous runs
    processed_files_path = os.path.join(folder_path, "processed_files.txt")
    if os.path.exists(processed_files_path):
        async with aiofiles.open(processed_files_path, 'r') as f:
            processed_files = set((await f.read()).splitlines())

    files_to_process = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                input_file = os.path.join(root, file)
                if os.path.getsize(input_file) > 1 * 1024 * 1024 and input_file not in processed_files:  # Check if file is larger than 1MB
                    files_to_process.append((input_file, root, processed_files))

    # Use ThreadPoolExecutor to process files in parallel with a limit on the number of workers
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(executor, sync_process_file, file_info) for file_info in files_to_process]
        results = await asyncio.gather(*tasks)

    for result in results:
        input_file, new_size, error = result
        if error:
            print(f"Failed to compress {input_file}: {error}")
            failed_files.append(input_file)
        else:
            print(f"Compressed {input_file}")
            changed_files.append((input_file, new_size))

    # Save the list of changed files and their sizes
    async with aiofiles.open(os.path.join(folder_path, "changed_files.txt"), 'w') as f:
        for original_file, new_size in changed_files:
            await f.write(f"{original_file} -> {new_size} bytes\n")
    
    # Save the list of processed files
    async with aiofiles.open(processed_files_path, 'w') as f:
        for processed_file in processed_files:
            await f.write(f"{processed_file}\n")

    # Save the list of failed files
    async with aiofiles.open(os.path.join(folder_path, "failed_files.txt"), 'w') as f:
        for failed_file in failed_files:
            await f.write(f"{failed_file}\n")

if __name__ == "__main__":
    folder_path = "./"
    asyncio.run(compress_pdfs_in_folder(folder_path, max_workers=2))
