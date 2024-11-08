from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config import get_access_token
from utils import get_files_to_upload
from onedrive_client import OneDriveClient
from dotenv import load_dotenv
import subprocess

load_dotenv()

def main():
    access_token = get_access_token()
    if not access_token:
        subprocess.Popen(['uvicorn', 'server:app', '--reload'])
        print("Please authenticate by visiting the authorization URL.")
        auth_url = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"client_id={os.getenv('CLIENT_ID')}&response_type=code&redirect_uri={os.getenv('REDIRECT_URI')}&"
            "scope=Files.ReadWrite.All offline_access"
        )
        print(f"Visit this URL to authenticate: {auth_url}")
        return

    FOLDER_PATH = Path(os.getenv('SOURCE_FOLDER'))
    CRITERIA = '*.csv'
    TARGET_PATH = os.getenv('TARGET_FOLDER')
    RECURSIVE = os.getenv('RECURSIVE', 'False').lower() in ('true', '1', 't')
    VERBOSE = os.getenv('VERBOSE', 'False').lower() in ('true', '1', 't')

    client = OneDriveClient(access_token)
    files_to_upload = get_files_to_upload(FOLDER_PATH, CRITERIA, RECURSIVE)
    if VERBOSE: print("Items to upload: ", len(files_to_upload), "files")
    
    client.create_folders(FOLDER_PATH, TARGET_PATH, verbose=VERBOSE)

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

                for future in as_completed(futures):
                    future.result()
                futures.clear()

if __name__ == "__main__":
    main()