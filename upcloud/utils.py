
def get_files_to_upload(folder_path, criteria, recursive=False): list(folder_path.rglob(criteria)) if recursive else list(folder_path.glob(criteria))
