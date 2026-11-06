from pathlib import Path

from conftest import file_item
from upcloud.onedrive_client import OneDriveClient
from upcloud.upcloud import target_folder_for
from upcloud.utils import get_files_to_upload

ITEM = "https://graph.microsoft.com/v1.0/me/drive/root:/"


def make_tree(root):
    (root / "sub").mkdir()
    for rel in ("a.csv", "b.parquet", "notes.txt", "sub/c.csv"):
        (root / rel).write_bytes(b"x")


def test_default_glob_takes_every_file_not_only_csv(tmp_path):
    make_tree(tmp_path)
    names = [p.relative_to(tmp_path).as_posix() for p in get_files_to_upload(tmp_path)]
    assert names == ["a.csv", "b.parquet", "notes.txt"]


def test_recursive_and_explicit_glob(tmp_path):
    make_tree(tmp_path)
    all_files = [p.relative_to(tmp_path).as_posix() for p in get_files_to_upload(tmp_path, recursive=True)]
    assert all_files == ["a.csv", "b.parquet", "notes.txt", "sub/c.csv"]
    csv = [p.name for p in get_files_to_upload(tmp_path, "*.csv", recursive=True)]
    assert csv == ["a.csv", "c.csv"]


def test_target_folder_for_keeps_relative_layout(tmp_path):
    assert target_folder_for("datasets/x", tmp_path, tmp_path / "a.csv") == "datasets/x"
    assert target_folder_for("datasets/x/", tmp_path, tmp_path / "sub" / "c.csv") == "datasets/x/sub"


def test_exists_checks_return_false_on_404_instead_of_raising(rsps):
    client = OneDriveClient("test-token")
    rsps.get(ITEM + "T/new.csv", status=404)
    rsps.get(ITEM + "T/old.csv", json=file_item("old.csv", 3))
    assert client.file_exists("new.csv", "T") is False
    assert client.file_exists("old.csv", "T") is True
    assert client.folder_exists("old.csv", "T") is False
