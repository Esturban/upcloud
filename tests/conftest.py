import os
import sys
from pathlib import Path

import pytest
import responses as responses_lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Never load the developer's real .env during tests.
os.environ["UPCLOUD_NO_DOTENV"] = "1"

GRAPH = "https://graph.microsoft.com/v1.0/me/drive"


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    for key in ("CLIENT_ID", "AZURE_VALUE", "REDIRECT_URI", "AZURE_REDIRECT_URI", "SCOPES",
                "SOURCE_FOLDER", "TARGET_FOLDER", "RECURSIVE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("CLIENT_ID", "test-client")
    monkeypatch.setenv("CACHED_TOKEN_PATH", str(tmp_path / "token_cache.json"))
    # Never touch the real roots file or move log.
    monkeypatch.setenv("UPCLOUD_ROOTS", str(tmp_path / "no-roots.tsv"))
    monkeypatch.setenv("UPCLOUD_MOVE_LOG", str(tmp_path / "moves.jsonl"))
    from upcloud import config
    config.Config.reload()
    yield
    config.Config.reload()


@pytest.fixture
def rsps():
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as mock:
        yield mock


@pytest.fixture
def sleeps():
    return []


@pytest.fixture
def client(sleeps):
    from upcloud.onedrive_client import OneDriveClient
    return OneDriveClient("test-token", sleep=sleeps.append)


def file_item(name, size, qxh=None, path="", item_id=None):
    item = {"id": item_id or f"id-{name}", "name": name, "size": size, "file": {"hashes": {}}}
    if qxh:
        item["file"]["hashes"]["quickXorHash"] = qxh
    return item


def folder_item(name, item_id=None, size=0):
    return {"id": item_id or f"id-{name}", "name": name, "size": size, "folder": {"childCount": 1}}
