from pathlib import Path

DEFAULT_GLOB = "*"  # every file; was hard-coded to *.csv


def get_files_to_upload(folder_path, criteria=DEFAULT_GLOB, recursive=False):
    """Files under folder_path whose name matches criteria, sorted."""
    folder_path = Path(folder_path)
    found = folder_path.rglob(criteria) if recursive else folder_path.glob(criteria)
    return sorted(p for p in found if p.is_file())
