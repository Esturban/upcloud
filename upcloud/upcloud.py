import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from .config import get_access_token, load_env
from .onedrive_client import OneDriveClient
from .utils import DEFAULT_GLOB, get_files_to_upload

WORKERS = 8


def target_folder_for(target_root, local_root, file_path):
    rel = Path(file_path).parent.relative_to(local_root).as_posix()
    return target_root if rel == "." else f"{target_root.rstrip('/')}/{rel}"


def main():
    load_env()
    access_token = get_access_token()

    FOLDER_PATH = Path(os.getenv('SOURCE_FOLDER'))
    CRITERIA = os.getenv('GLOB', DEFAULT_GLOB)
    TARGET_PATH = os.getenv('TARGET_FOLDER')
    RECURSIVE = os.getenv('RECURSIVE', 'False').lower() in ('true', '1', 't')
    VERBOSE = os.getenv('VERBOSE', 'False').lower() in ('true', '1', 't')
    client = OneDriveClient(access_token)
    files_to_upload = get_files_to_upload(FOLDER_PATH, CRITERIA, RECURSIVE)
    if VERBOSE: print("Items to upload: ", len(files_to_upload), "files")

    client.create_folders(FOLDER_PATH, TARGET_PATH, verbose=VERBOSE)

    def check_and_upload(file_path):
        target_folder = target_folder_for(TARGET_PATH, FOLDER_PATH, file_path)
        if not client.file_exists(file_path.name, target_folder):
            client.upload_file(file_path, target_folder)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor, \
            tqdm(total=len(files_to_upload), desc="Uploading") as pbar:
        futures = [executor.submit(check_and_upload, f) for f in files_to_upload]
        for future in as_completed(futures):
            future.result()
            pbar.update(1)


if __name__ == "__main__":
    main()
