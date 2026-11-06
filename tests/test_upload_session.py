import os

import responses

from conftest import file_item
from upcloud.mirror import _redact, plan_mirror
from upcloud.onedrive_client import OneDriveClient

ROOT = "https://graph.microsoft.com/v1.0/me/drive/root"
SESSION = "https://my.microsoftpersonalcontent.com/up/abc?tempauth=SECRETTOKEN"


def test_large_upload_chunks_go_without_auth_header_and_replace(rsps, tmp_path):
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (5 * 1024 * 1024))
    os.utime(big, (1_700_000_000, 1_700_000_000))
    rsps.post(f"{ROOT}:/B/big.bin:/createUploadSession", json={"uploadUrl": SESSION})
    rsps.put(SESSION, status=201, json={})
    OneDriveClient("t").upload_file(big, "B")
    session_body = rsps.calls[0].request.body.decode()
    assert '"replace"' in session_body
    assert "2023-11-14T22:13:20Z" in session_body  # local mtime kept on OneDrive
    puts = [c.request for c in rsps.calls if c.request.method == "PUT"]
    assert puts and all("Authorization" not in r.headers for r in puts)


def test_empty_onedrive_placeholder_is_uploaded_not_newer(rsps, tmp_path):
    (tmp_path / "log.txt").write_bytes(b"real content")
    placeholder = file_item("log.txt", 0)
    placeholder["fileSystemInfo"] = {"lastModifiedDateTime": "2026-11-06T10:00:00Z"}
    rsps.get(f"{ROOT}:/B", json={"id": "b", "name": "B", "folder": {}})
    rsps.get(f"{ROOT}:/B:/children", json={"value": [placeholder]})
    assert [a.kind for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")] == ["upload"]


def test_redact_strips_preauthenticated_query_strings():
    msg = f"401 Client Error: Unauthorized for url: {SESSION}"
    assert "SECRETTOKEN" not in _redact(msg)


def test_small_upload_quotes_ampersand_names(rsps, tmp_path):
    f = tmp_path / " Q&A #1.docx"
    f.write_bytes(b"doc")
    rsps.put(f"{ROOT}:/B/%20Q%26A%20%231.docx:/content", status=201, json={})
    OneDriveClient("t").upload_file(f, "B")
    assert len(rsps.calls) == 1
