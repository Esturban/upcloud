from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config import get_access_token
from utils import get_files_to_upload
from onedrive_client import OneDriveClient
from dotenv import load_dotenv
load_dotenv()

def main():
        # Replace with the paths to the files you want to upload
    FOLDER_PATH = Path(os.getenv('SOURCE_FOLDER'))
    CRITERIA = '*.csv'
    TARGET_PATH = os.getenv('TARGET_FOLDER')  # Replace with your target folder in OneDrive
    RECURSIVE = os.getenv('RECURSIVE', 'False').lower() in ('true', '1', 't')
    VERBOSE = os.getenv('VERBOSE', 'False').lower() in ('true', '1', 't')

    access_token = get_access_token()
    client = OneDriveClient(access_token)
    files_to_upload = get_files_to_upload(FOLDER_PATH, CRITERIA, RECURSIVE)
    if VERBOSE: print("Items to upload: ", len(files_to_upload), "files")
    
    client.create_folders(FOLDER_PATH, TARGET_PATH,verbose=VERBOSE)
    

    # Upload files folder by folder
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for root, _, files in os.walk(FOLDER_PATH):
            relative_root = Path(root).relative_to(FOLDER_PATH)
            target_folder = TARGET_PATH / relative_root

            with tqdm(total=len(files), desc=f"Uploading files in {relative_root}") as pbar:
                for file_name in files:
                    file_path = Path(root) / file_name

                    def check_and_upload(file_path, target_folder):
                        if not client.file_exists(file_path.name, target_folder):
                            client.upload_file(file_path, target_folder)
                        pbar.update(1)

                    futures.append(executor.submit(check_and_upload, file_path, target_folder))

                # Wait for the current folder to complete
                for future in as_completed(futures):
                    future.result()
                futures.clear()

if __name__ == "__main__":
    main()