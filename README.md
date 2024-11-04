# Upcloud

Upcloud is a Python script that uploads all files from a specified local folder to a target folder in OneDrive. It supports both simple and resumable uploads, ensuring efficient file transfer.

## Requirements

- Python 3.6 or higher
- `requests` library
- `pyjwt` library
- `adal` library
- `onelogin` library

## Setup

1. **Azure AD Application Setup**:
    - Create an Azure AD application.
    - Add the OneDrive API permissions to the application.
    - Create a client secret for the application.

2. **Environment Variables**:
    - Create a `.env` file in the project root with the following variables:
      ```env
      CLIENT_ID=<your_azure_ad_application_id>
      CLIENT_SECRET=<your_azure_ad_application_secret>
      TENANT_ID=<your_azure_ad_tenant_id>
      SOURCE_FOLDER=<local_source_folder_path>
      TARGET_FOLDER=<onedrive_target_folder_path>
      ```

## Usage

1. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the Script**:
    ```sh
    python upload.py --source_folder <local_source_folder_path> --target_folder <onedrive_target_folder_path> --client_id <your_azure_ad_application_id> --client_secret <your_azure_ad_application_secret> --tenant_id <your_azure_ad_tenant_id>
    ```

## Example

```sh
python  --source_folder ./local_folder --target_folder /OneDriveFolder --client_id your_client_id --client_secret your_client_secret --tenant_id your_tenant_id
```


### Project Structure

```sh
.
├── README.md
├── local.env
├── requirements.txt
└── upcloud
    ├── __init__.py
    ├── config.py
    ├── onedrive_client.py
    ├── upcloud.py
    └── utils.py

```

### Key Functions  

- File Existence Check:

	- `file_exists_on_onedrive(file_name, access_token, folder_name=None)` in `upcloud/utils.py`
	- `file_exists(self, file_name, folder_name=None)` in `upcloud/onedrive_client.py`  

- Folder Existence Check:  

	- `folder_exists_on_onedrive(folder_name, access_token, parent_folder=None)` in `upcloud/utils.py`
	- `folder_exists(self, folder_name, parent_folder=None)` in `upcloud/onedrive_client.py`

- File Upload:

	- `upload_file(self, file_path, target_location=None, verbose=None)` in `upcloud/onedrive_client.py`
	- `upload_file_in_chunks(self, file_path, upload_url)` in `upcloud/onedrive_client.py`

- Folder Creation:

	- `create_folder(self, folder_name, parent_folder=None)` in `upcloud/onedrive_client.py`

- Resumable Upload Session:

	- `initiate_resumable_upload_session(self, file_path, target_location=None)` in `upcloud/onedrive_client.py`

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.