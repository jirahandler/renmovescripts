import os

def list_unique_underscore_extensions(root_folder):
    unique_extensions = set()

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if '_' in filename and '.' not in filename.split('_')[-1]:
                parts = filename.rsplit('_', 1)
                if len(parts) > 1:
                    unique_extensions.add(parts[1])

    return unique_extensions

def main():
    root_folder = '.'  # Change this to your target folder
    unique_extensions = list_unique_underscore_extensions(root_folder)
    
    print("Unique parts after the last underscore in filenames:")
    for ext in unique_extensions:
        print(ext)

if __name__ == "__main__":
    main()
