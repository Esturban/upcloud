import requests
import os

class OneDriveClient:
    def __init__(self, access_token):
        self.access_token = access_token

    def _get_headers(self, content_type='application/json'):
        return {'Authorization': f'Bearer {self.access_token}', 'Content-Type': content_type}

    def _make_request(self, method, url, headers=None, **kwargs):
        headers = headers or self._get_headers()
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def create_folder(self, folder_name,  parent_folder=None):
        """Create a folder on OneDrive.

        Args:
            parent_folder (str): Parent folder for the new folder.
            folder_path (str): Name of the folder to create.

        Returns:
            str: ID of the created folder.
        """
        create_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}:/children' if parent_folder else 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        data = {'name': folder_name, 'folder': {}, '@microsoft.graph.conflictBehavior': 'rename'}
        response=self._make_request('POST', create_url, json=data)
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
        # Get all directories in the local folder that need to be created in the target folder
        directories_to_create = [os.path.join(target_folder, os.path.relpath(root, local_folder)).replace("\\", "/") for root, dirs, files in os.walk(local_folder) if files or dirs]
        for onedrive_path in sorted(directories_to_create):
            if verbose: print(f'Checking folder {onedrive_path}')
            if not self.folder_exists(onedrive_path):
                self.create_folder(os.path.basename(onedrive_path), os.path.dirname(onedrive_path))
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
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}/{folder_name}' if parent_folder else f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}'
        return self._make_request('GET', check_url).status_code == 200

    def file_exists(self, file_name, folder_name=None):
        """
        Check if a file exists on OneDrive.

        Args:
            file_name (str): Name of the file to check.
            folder_name (str, optional): Parent folder of the file. Defaults to None.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}/{file_name}' if folder_name else f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}'
        return self._make_request('GET', check_url).status_code == 200

    def initiate_resumable_upload_session(self, file_path, target_location=None):
        """
        Initiate a resumable upload session for a file on OneDrive.

        Args:
            file_path (str): Path to the file to upload.
            target_location (str, optional): Target folder for the file. Defaults to None.

        Returns:
            str: Upload URL for the file.
        """
        upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/createUploadSession' if target_location else f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/createUploadSession'
        data = {'item': {'@microsoft.graph.conflictBehavior': 'rename', 'name': file_path.name}}
        return self._make_request('POST', upload_url, json=data).json()['uploadUrl']

    def upload_file_in_chunks(self, file_path, upload_url):
        """
        Upload a file in chunks.

        Args:
            file_path (str): Path to the file to upload.
            upload_url (str): Upload URL for the file
        """
        chunk_size, file_size = 327680, os.path.getsize(file_path)
        with open(file_path, 'rb') as file:
            for chunk_start in range(0, file_size, chunk_size):
                chunk_end = min(chunk_start + chunk_size, file_size) - 1
                file.seek(chunk_start)
                chunk_data = file.read(chunk_end - chunk_start + 1)
                headers = self._get_headers()
                headers['Content-Range'] = f'bytes {chunk_start}-{chunk_end}/{file_size}'
                self._make_request('PUT', upload_url, headers=headers, data=chunk_data)

    def upload_file(self, file_path, target_location=None, verbose=None):
        """
        Upload a file to OneDrive.

        Args:
            file_path (str): Path to the file to upload.
            target_location (str, optional): Target folder for the file. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to None.
        """
        file_size = os.path.getsize(file_path)
        if file_size <= 4 * 1024 * 1024:
            upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/content' if target_location else f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/content'
            with open(file_path, 'rb') as file:
                response = self._make_request('PUT', upload_url, headers=self._get_headers('application/octet-stream'), data=file)
            if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"}.' if response.status_code == 201 else f'Failed to upload {file_path.name}. Status code: {response.status_code}, Response: {response.text}')
        else:
            upload_url = self.initiate_resumable_upload_session(file_path, target_location)
            self.upload_file_in_chunks(file_path, upload_url)
            if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"} using resumable upload.')

    def download_file(self, file_path=None, target_location=None, item_id=None, drive_id=None, site_id=None, group_id=None, share_id=None, user_id=None, verbose=None):
        """ Download a file from OneDrive.

        Args:
            file_path (str, optional): Path to the file to download. Defaults to None.
            target_location (str, optional): Target folder for the file. Defaults to None.
            item_id (str, optional): Item ID for one drive. Defaults to None.
            drive_id (str, optional): Drive ID. Defaults to None.
            site_id (str, optional): Site ID. Defaults to None.
            group_id (str, optional): Group ID. Defaults to None.
            share_id (str, optional): Share ID. Defaults to None.
            user_id (str, optional): User ID. Defaults to None.
            verbose (str, optional): Whether to print verbose output. Defaults to None.

        Raises:
            ValueError: Invalid combination of parameters for file access

        Returns:
        Tuple[int, int]: Number of bytes downloaded and total file size.
        """
        base_url = "https://graph.microsoft.com/v1.0"
        if file_path: url = f"{base_url}/me/drive/root:/{file_path}:/contentStream"
        elif item_id and drive_id: url = f"{base_url}/drives/{drive_id}/items/{item_id}/contentStream"
        elif item_id and group_id: url = f"{base_url}/groups/{group_id}/drive/items/{item_id}/contentStream"
        elif item_id: url = f"{base_url}/me/drive/items/{item_id}/contentStream"
        elif share_id: url = f"{base_url}/shares/{share_id}/driveItem/contentStream"
        elif item_id and site_id: url = f"{base_url}/sites/{site_id}/drive/items/{item_id}/contentStream"
        elif item_id and user_id: url = f"{base_url}/users/{user_id}/drive/items/{item_id}/contentStream"
        else: raise ValueError("Invalid combination of parameters for file access")
        response = self._make_request('GET', url, headers=self._get_headers('application/octet-stream'), stream=True)
        file_size = int(response.headers.get('content-length', 0))
        return self._handle_download(response, target_location, file_size, verbose)
    
    def _handle_download(self, response, target_location, file_size, verbose):
        return self.download_file_in_chunks(response, target_location, file_size, verbose) if file_size > 4194304 else self._direct_download(response, target_location, verbose)

    def _direct_download(self, response, target_location, verbose):
        with open(target_location, 'wb') as f: f.write(response.content)
        if verbose: print(f'Downloaded to {target_location}')
        return len(response.content), len(response.content)

    def download_file_in_chunks(self, response, target_location, file_size, verbose=None):
        chunk_size, bytes_downloaded = 327680, 0
        with open(target_location, 'wb') as f:
            for chunk in response.iter_content(chunk_size):
                if not chunk: continue
                bytes_downloaded += len(chunk)
                f.write(chunk)
                if verbose and file_size: print(f'\rProgress: {(bytes_downloaded/file_size)*100:.1f}%', end='', flush=True)
        if verbose: print(f'\nDownloaded {bytes_downloaded}/{file_size} bytes to {target_location}')
        return bytes_downloaded, file_size