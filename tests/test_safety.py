import json

import pytest

from upcloud.movelog import log_move, log_path
from upcloud.safety import is_sensitive


@pytest.mark.parametrize("name", [".env", ".env.local", "server.pem", "id.KEY", "my_Token.json",
                                  "Tax-2024.pdf", "bank.csv", "Invoice 12.pdf", "statement-oct.pdf"])
def test_secret_and_financial_names_are_sensitive(name):
    assert is_sensitive(name)


@pytest.mark.parametrize("name", ["photo.jpg", "notes.txt", "keyboard.md", "environment.txt"])
def test_ordinary_names_are_not(name):
    assert not is_sensitive(name)


def test_a_sensitive_folder_makes_everything_inside_sensitive():
    assert is_sensitive("Taxes/2024/scan.pdf") and is_sensitive("a/bank statements/x.png")
    assert not is_sensitive("holiday/2024/scan.pdf")


def test_mirror_never_uploads_sensitive_files(tmp_path):
    from upcloud.mirror import scan_local
    for name in (".env", "cert.pem", "tax-return.pdf", "ok.txt"):
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / "bank").mkdir()
    (tmp_path / "bank" / "inside.txt").write_bytes(b"x")
    assert list(scan_local(tmp_path)) == ["ok.txt"]


def test_log_move_appends_one_json_line_per_step():
    log_move("offload", src="/a/b", status="trashed")
    log_move("mv", src="x", dst="y", status="ok")
    lines = log_path().read_text().splitlines()
    first, second = json.loads(lines[0]), json.loads(lines[1])
    assert first["verb"] == "offload" and first["status"] == "trashed" and "ts" in first
    assert second["dst"] == "y"


def test_mirror_skips_symlinks_so_a_link_cannot_smuggle_a_secret(tmp_path):
    from upcloud.mirror import scan_local
    (tmp_path / ".env").write_bytes(b"k")
    (tmp_path / "notes.txt").symlink_to(tmp_path / ".env")
    (tmp_path / "ok.txt").write_bytes(b"x")
    assert list(scan_local(tmp_path)) == ["ok.txt"]
