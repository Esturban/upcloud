import os

from conftest import file_item, folder_item
from upcloud import cli
from upcloud.mirror import apply_plan, plan_mirror
from upcloud.onedrive_client import OneDriveClient
from upcloud.quickxor import quickxor_file

ROOT = "https://graph.microsoft.com/v1.0/me/drive/root"


def item(path):
    return f"{ROOT}:/{path}"


def children(path):
    return f"{ROOT}:/{path}:/children"


def make_tree(root):
    (root / "sub").mkdir()
    (root / "same.csv").write_bytes(b"same")
    (root / "edited.csv").write_bytes(b"edit")
    (root / "grown.csv").write_bytes(b"grown!")
    (root / "notes.txt").write_bytes(b"txt")
    (root / "sub" / "new.parquet").write_bytes(b"pq")


def remote_tree(rsps, root):
    rsps.get(item("B"), json=folder_item("B"))
    rsps.get(children("B"), json={"value": [
        file_item("same.csv", 4, quickxor_file(root / "same.csv")),
        file_item("edited.csv", 4, "AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
        file_item("grown.csv", 3),
        file_item("old.csv", 9),
    ]})


def test_plan_skips_by_size_and_hash_and_reports_extras(rsps, tmp_path):
    make_tree(tmp_path)
    remote_tree(rsps, tmp_path)
    plan = {a.rel: (a.kind, a.reason) for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")}
    assert plan == {
        "same.csv": ("skip", "same size and hash"),
        "edited.csv": ("upload", "changed content"),
        "grown.csv": ("upload", "changed size"),
        "notes.txt": ("upload", "new"),
        "sub/new.parquet": ("upload", "new"),
        "old.csv": ("extra", "only on OneDrive, left alone"),
    }


def test_plan_against_missing_target_uploads_everything(rsps, tmp_path):
    make_tree(tmp_path)
    rsps.get(item("B"), status=404)
    assert {a.kind for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")} == {"upload"}


def test_apply_creates_missing_parents_uploads_and_never_deletes(rsps, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.csv").write_bytes(b"a")
    client = OneDriveClient("t")
    rsps.get(item("datasets/x"), status=404)
    plan = plan_mirror(client, tmp_path, "datasets/x")
    for path in ("datasets", "datasets/x", "datasets/x/sub"):
        rsps.get(item(path), status=404)
    rsps.post(f"{ROOT}/children", status=201, json=folder_item("datasets"))
    rsps.post(children("datasets"), status=201, json=folder_item("x"))
    rsps.post(children("datasets/x"), status=201, json=folder_item("sub"))
    rsps.put(f"{ROOT}:/datasets/x/sub/a.csv:/content", status=201, json=file_item("a.csv", 1))
    result = apply_plan(client, "datasets/x", plan)
    assert result.uploaded == ["sub/a.csv"] and result.failed == []
    posts = [c.request.url for c in rsps.calls if c.request.method == "POST"]
    assert posts == [f"{ROOT}/children", children("datasets"), children("datasets/x")]
    assert not any(c.request.method == "DELETE" for c in rsps.calls)


def test_mirror_cli_defaults_to_dry_run_from_env(monkeypatch, rsps, tmp_path, capsys):
    (tmp_path / "a.csv").write_bytes(b"a")
    monkeypatch.setenv("SOURCE_FOLDER", str(tmp_path))
    monkeypatch.setenv("TARGET_FOLDER", "datasets/multi_issn")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("datasets/multi_issn"), status=404)
    assert cli.main(["mirror"]) == 0
    out = capsys.readouterr().out
    assert "upload   a.csv  (new, 1 B)" in out and "Dry run: nothing changed" in out
    assert all(c.request.method == "GET" for c in rsps.calls)


def test_mirror_cli_apply_uploads_and_exits_5_on_failure(monkeypatch, rsps, tmp_path, capsys):
    (tmp_path / "a.csv").write_bytes(b"a")
    (tmp_path / "b.csv").write_bytes(b"b")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("B"), json=folder_item("B"))
    rsps.get(children("B"), json={"value": []})
    rsps.put(f"{ROOT}:/B/a.csv:/content", status=201, json=file_item("a.csv", 1))
    rsps.put(f"{ROOT}:/B/b.csv:/content", status=500)
    assert cli.main(["mirror", str(tmp_path), "B", "--apply"]) == 5
    captured = capsys.readouterr()
    assert "1 uploaded, 1 failed" in captured.out
    assert "failed   b.csv" in captured.err


def test_mirror_without_src_or_env_exits_2(capsys):
    assert cli.main(["mirror"]) == 2
    assert "SOURCE_FOLDER" in capsys.readouterr().err


def test_plan_leaves_a_newer_onedrive_copy_alone(rsps, tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"old local")
    os.utime(tmp_path / "doc.pdf", (1_700_000_000, 1_700_000_000))  # 2023-11
    newer = file_item("doc.pdf", 3)
    newer["fileSystemInfo"] = {"lastModifiedDateTime": "2026-10-02T10:00:00Z"}
    rsps.get(item("B"), json=folder_item("B"))
    rsps.get(children("B"), json={"value": [newer]})
    plan = {a.rel: (a.kind, a.reason) for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")}
    assert plan == {"doc.pdf": ("newer", "OneDrive copy is newer, left alone")}


def test_plan_ignores_macos_junk_files(rsps, tmp_path):
    (tmp_path / ".DS_Store").write_bytes(b"x")
    (tmp_path / "._photo.jpg").write_bytes(b"x")
    (tmp_path / "photo.jpg").write_bytes(b"jpg")
    rsps.get(item("B"), status=404)
    assert [a.rel for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")] == ["photo.jpg"]


def test_plan_uploads_when_onedrive_copy_is_older(rsps, tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"new local")
    older = file_item("doc.pdf", 3)
    older["fileSystemInfo"] = {"lastModifiedDateTime": "2020-01-01T00:00:00.5Z"}
    rsps.get(item("B"), json=folder_item("B"))
    rsps.get(children("B"), json={"value": [older]})
    assert [a.kind for a in plan_mirror(OneDriveClient("t"), tmp_path, "B")] == ["upload"]
