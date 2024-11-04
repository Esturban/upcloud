import requests
import os
def create_folder_on_onedrive(folder_name, access_token, parent_folder=None):
    """Create a folder on OneDrive.

    Args:
        folder_name (str): Name of the folder to create.
        access_token (str): Access token for the user.
        parent_folder (str, optional): Parent folder for the new folder. Defaults to None.

    Returns:
        str: ID of the created folder.
    """
    if parent_folder:
        create_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}:/children'
    else:
        create_url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': folder_name,
        'folder': {},
        '@microsoft.graph.conflictBehavior': 'rename'
    }
    response = requests.post(create_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['id']

def folder_exists_on_onedrive(folder_name, access_token, parent_folder=None):
    """
    Check if a folder exists on OneDrive.

    Args:
        folder_name (str): Name of the folder to check.
        access_token (str): Access token for the user.
        parent_folder (str, optional): Parent folder for the new folder. Defaults to None.

    Returns:
        bool: True if the folder exists, False otherwise.
    """
    if parent_folder:
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{parent_folder}/{folder_name}'
    else:
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(check_url, headers=headers)
    return response.status_code == 200

def file_exists_on_onedrive(file_name, access_token, folder_name=None):
    """
    Check if a file exists on OneDrive.

    Args:
        file_name (str): Name of the file to check.
        access_token (str): Access token for the user.
        folder_name (str, optional): Parent folder of the file. Defaults to None.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if folder_name:
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{folder_name}/{file_name}'
    else:
        check_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(check_url, headers=headers)
    return response.status_code == 200


def initiate_resumable_upload_session(file_path, access_token, target_location=None):
    """
    Initiate a resumable upload session for a file on OneDrive.

    Args:
        file_path (str): Path to the file to upload.
        access_token (str): Access token for the user.
        target_location (str, optional): Target folder for the file. Defaults to None.

    Returns:
        str: Upload URL for the file.
    """
    if target_location:
        upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/createUploadSession'
    else:
        upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/createUploadSession'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
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

def upload_file_to_onedrive(file_path, access_token, target_location=None, verbose=None):
    """
    Upload a file to OneDrive.

    Args:
        file_path (str): Path to the file to upload.
        access_token (str): Access token for the user.
        target_location (str, optional): Target folder for the file on OneDrive. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to None.
    """
    if target_location:
        upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{target_location}/{file_path.name}:/content'
    else:
        upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_path.name}:/content'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, headers=headers, data=file)
    if response.status_code == 201:
        if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"}.')
    else:
        print(f'Failed to upload {file_path.name}. Status code: {response.status_code}, Response: {response.text}')


def upload_file_in_chunks(file_path, upload_url):
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

def upload_file_to_onedrive(file_path, access_token, target_location=None, verbose=None):
    """
    Upload a file to OneDrive.

    Args:
        file_path (str): Path to the file to upload.
        access_token (str): Access token for the user.
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
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        with open(file_path, 'rb') as file:
            response = requests.put(upload_url, headers=headers, data=file)
        if response.status_code == 201:
            if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"}.')
        #else:
        #    print(f'Failed to upload {file_path.name}. Status code: {response.status_code}, Response: {response.text}')
    else:
        upload_url = initiate_resumable_upload_session(file_path, access_token, target_location)
        upload_file_in_chunks(file_path, upload_url)
        if verbose: print(f'{file_path.name} uploaded successfully to {target_location if target_location else "root"} using resumable upload.')
