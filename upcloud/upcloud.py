from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from upcloud import get_access_token, OneDriveClient
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    # Replace with the paths to the files you want to upload
    FOLDER_PATH = Path(os.getenv('SOURCE_FOLDER'))
    CRITERIA = '*.csv'
    TARGET_LOCATION = os.getenv('TARGET_FOLDER')  # Replace with your target folder in OneDrive

    access_token = get_access_token()
    client = OneDriveClient(access_token)
    files_to_upload = list(FOLDER_PATH.glob(CRITERIA))
    print("Items to upload: ", len(files_to_upload), "files")

    # Create necessary folders up front
    batches = [files_to_upload[i:i+5000] for i in range(0, len(files_to_upload), 5000)]
    #num_last_batches = 3

    # Get the last few batches using slicing
    #last_batches = batches[-num_last_batches:]

    # Enumerate over the last few batches
    folder_names = []
    #for i, batch in enumerate(last_batches, start=len(batches) - num_last_batches):
    for i, batch in enumerate(batches):
        folder_name = f'{i+1}'
        if not client.folder_exists(folder_name, TARGET_LOCATION):
            client.create_folder(folder_name, TARGET_LOCATION)
            print(f'Created folder {folder_name}')
        else:
            print(f'Folder {folder_name} already exists')
        folder_names.append(folder_name)

    # Upload files in batches
    with ThreadPoolExecutor(max_workers=8) as executor:
        #for i, batch in enumerate(last_batches, start=len(batches) - num_last_batches):
        #    folder_name = folder_names[i - (len(batches) - num_last_batches)]
        for i, batch in enumerate(batches):
            with tqdm(total=len(batch), desc=f"Processing batch {i+1} to OneDrive") as pbar:
                futures = []
                for file_path in batch:
                    def check_and_upload(file_path, folder_name):
                        if not client.file_exists(file_path.name, f'{TARGET_LOCATION}/{folder_name}'):
                            #print(f'Uploading {file_path.name} to {folder_name}')
                            client.upload_file(file_path, f'{TARGET_LOCATION}/{folder_name}')
                        #else:
                            #print(f'Skipping {file_path.name}, already exists in {folder_name}')
                        pbar.update(1)
                    
                    futures.append(executor.submit(check_and_upload, file_path, folder_name))
                
                # Wait for the current batch to complete
                for future in as_completed(futures):
                    future.result()
                futures.clear()