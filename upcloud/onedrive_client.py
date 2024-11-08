import requests
import os

class OneDriveClient:
    def __init__(self, access_token):
        self.access_token = access_token

    def create_folder(self, folder_name,  parent_folder=None):
        """Create a folder on OneDrive.

        Args:
            parent_folder (str): Parent folder for the new folder.
            folder_path (str): Name of the folder to create.

        Returns:
            str: ID of the created folder.
        """
        if parent_folder:
            create_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}:/children'
        else:
            create_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': folder_name,
            'folder': {},
            '@microsoft.graph.conflictBehavior': 'rename'
        }
        
        response = requests.post(create_url, headers=headers, json=data)
        if response.status_code != 201:
            print(create_url)
            print(data)
            print(f"Failed to create folder: {folder_name} in {parent_folder}")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.content}")
        response.raise_for_status()
        return response.json()['id']
    def create_folders(self, local_folder,target_folder,verbose=None):
        """Create multiple folders on OneDrive.
        Args:
            local_folder (list): List of folder names to create.
            target_folder (str, optional): Parent folder for the new folders. Defaults to None.
        """
        
        # Gather all directories that need to be created
        directories_to_create = []
        for root, dirs, files in os.walk(local_folder):
            if not files and not dirs:
                continue  # Skip empty directories

            relative_path = os.path.relpath(root, local_folder)
            onedrive_path = os.path.join(target_folder, relative_path).replace("\\", "/")
            directories_to_create.append(onedrive_path)

        # Sort directories to ensure parent directories are created first
        directories_to_create.sort()

        # Create each directory incrementally
        for onedrive_path in directories_to_create:
            if verbose: print(f'Checking folder {onedrive_path}')
            if not self.folder_exists(onedrive_path):
                parent_folder = os.path.dirname(onedrive_path)
                folder_name = os.path.basename(onedrive_path)
                self.create_folder(folder_name,parent_folder)
                if verbose: print(f'Created folder {onedrive_path}')
            else:
                if verbose: print(f'Folder {onedrive_path} already exists')
    def folder_exists(self, folder_name, parent_folder=None):
        """
        Check if a folder exists on OneDrive.

        Args:
            folder_name (str): Name of the folder to check.
            parent_folder (str, optional): Parent folder for the new folder. Defaults to None.

        Returns:
            bool: True if the folder exists, False otherwise.
        """
        if parent_folder:
            check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}/{folder_name}'
        else:
            check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}'
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(check_url, headers=headers)
        return response.status_code == 200

    def file_exists(self, file_name, folder_name=None):
        """
        Check if a file exists on OneDrive.

        Args:
            file_name (str): Name of the file to check.
            folder_name (str, optional): Parent folder of the file. Defaults to None.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        if folder_name:
            check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}/{file_name}'
        else:
            check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}'
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(check_url, headers=headers)
        return response.status_code == 200

    def initiate_resumable_upload_session(self, file_path, target_location=None):
        """
        Initiate a resumable upload session for a file on OneDrive.

        Args:
            file_path (str): Path to the file to upload.
            target_location (str, optional): Target folder for the file. Defaults to None.

        Returns:
            str: Upload URL for the file.
        """
        if target_location:
            upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/createUploadSession'
        else:
            upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/createUploadSession'
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'item': {
                '@microsoft.graph.conflictBehavior': 'rename',
                'name': file_path.name
            }
        }
        response = requests.post(upload_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['uploadUrl']

    def upload_file_in_chunks(self, file_path, upload_url):
        """
        Upload a file in chunks.

        Args:
            file_path (str): Path to the file to upload.
            upload_url (str): Upload URL for the file
        """
        chunk_size = 327680  # 320KB
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file:
            for chunk_start in range(0, file_size, chunk_size):
                chunk_end = min(chunk_start + chunk_size, file_size) - 1
                file.seek(chunk_start)
                chunk_data = file.read(chunk_end - chunk_start + 1)
                headers = {
                    'Content-Range': f'bytes {chunk_start}-{chunk_end}/{file_size}'
                }
                response = requests.put(upload_url, headers=headers, data=chunk_data)
                response.raise_for_status()

    def upload_file(self, file_path, target_location=None, verbose=None):
        """
        Upload a file to OneDrive.

        Args:
            file_path (str): Path to the file to upload.
            target_location (str, optional): Target folder for the file. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to None.
        """
        file_size = os.path.getsize(file_path)
        if file_size <= 4 * 1024 * 1024:  # 4MB 
            if target_location:
                upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/content'
            else:
                upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/content'
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            with open(file_path, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
            if response.status_code == 201:
                if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"}.')
            else:
                print(f'Failed to upload {file_path.name}. Status code: {response.status_code}, Response: {response.text}')
        else:
            upload_url = self.initiate_resumable_upload_session(file_path, target_location)
            self.upload_file_in_chunks(file_path, upload_url)
            if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"} using resumable upload.')
    