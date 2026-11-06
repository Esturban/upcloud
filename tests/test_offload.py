import json
import os
import subprocess
import time

import pytest

from conftest import file_item, folder_item
from upcloud import cli, offload
from upcloud.movelog import log_path
from upcloud.onedrive_client import OneDriveClient
from upcloud.quickxor import quickxor_file

ROOT = "https://graph.microsoft.com/v1.0/me/drive/root"
DAY = 86400


def item(path):
    return f"{ROOT}:/{path}"


def children(path):
    return f"{ROOT}:/{path}:/children"


def old(path, days=400):
    stamp = time.time() - days * DAY
    os.utime(path, (stamp, stamp))


def write_roots(tmp_path, monkeypatch, local, cloud="Docs"):
    roots = tmp_path / "roots.tsv"
    roots.write_text(f"{local}\t{cloud}\n")
    monkeypatch.setenv("UPCLOUD_ROOTS", str(roots))


@pytest.fixture
def signed_in(monkeypatch):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))


@pytest.fixture
def trashed(monkeypatch):
    calls = []
    monkeypatch.setattr(offload, "trash_path", lambda p: calls.append(str(p)))
    return calls


def make_local(tmp_path):
    local = tmp_path / "docs"
    local.mkdir()
    for name, data in (("old_same.txt", b"aaaa"), ("recent.txt", b"bbbb"), ("hashdiff.txt", b"cccc"),
                       ("sizediff.txt", b"dd"), ("cloudless.txt", b"eeee"), ("nohash.txt", b"ffff"),
                       ("tax-2024.pdf", b"gggg")):
        (local / name).write_bytes(data)
        if name != "recent.txt":
            old(local / name)
    return local


def serve_remote(rsps, local):
    rsps.get(item("Docs"), json=folder_item("Docs"))
    rsps.get(children("Docs"), json={"value": [
        file_item("old_same.txt", 4, quickxor_file(local / "old_same.txt")),
        file_item("recent.txt", 4, quickxor_file(local / "recent.txt")),
        file_item("hashdiff.txt", 4, "AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
        file_item("sizediff.txt", 9, "AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
        file_item("nohash.txt", 4),
        file_item("tax-2024.pdf", 4, quickxor_file(local / "tax-2024.pdf")),
    ]})


def read_plan(path):
    return [line.split("\t") for line in path.read_text().splitlines() if not line.startswith("#")]


def test_review_lists_only_verified_old_files_and_writes_plan(tmp_path, monkeypatch, signed_in, rsps, capsys):
    local = make_local(tmp_path)
    write_roots(tmp_path, monkeypatch, local)
    serve_remote(rsps, local)
    plan = tmp_path / "plan.tsv"
    assert cli.main(["review", "--out", str(plan)]) == 0
    rows = read_plan(plan)
    assert [r[1] for r in rows] == ["Docs/old_same.txt"]
    assert rows[0][0] == str(local / "old_same.txt") and rows[0][2] == "4"
    assert rows[0][3] == quickxor_file(local / "old_same.txt")
    assert "1 files" in capsys.readouterr().out
    assert all(c.request.method == "GET" for c in rsps.calls)


def test_review_prints_gb_per_root(tmp_path, monkeypatch, signed_in, rsps, capsys):
    local = make_local(tmp_path)
    write_roots(tmp_path, monkeypatch, local)
    serve_remote(rsps, local)
    cli.main(["review", "--out", str(tmp_path / "plan.tsv")])
    assert f"{local} -> OneDrive:Docs: 1 files, 0.0 GB" in capsys.readouterr().out


def test_review_days_widens_the_window(tmp_path, monkeypatch, signed_in, rsps):
    local = make_local(tmp_path)
    old(local / "old_same.txt", days=100)
    write_roots(tmp_path, monkeypatch, local)
    serve_remote(rsps, local)
    plan = tmp_path / "plan.tsv"
    cli.main(["review", "--out", str(plan)])
    assert read_plan(plan) == []
    cli.main(["review", "--days", "90", "--out", str(plan)])
    assert [r[1] for r in read_plan(plan)] == ["Docs/old_same.txt"]


def test_review_without_roots_exits_2_with_fix(capsys):
    assert cli.main(["review"]) == 2
    assert "roots.tsv" in capsys.readouterr().err


def test_review_missing_root_folder_exits_4_and_continues(tmp_path, monkeypatch, signed_in, rsps, capsys):
    local = make_local(tmp_path)
    roots = tmp_path / "roots.tsv"
    roots.write_text(f"{tmp_path}/gone\tGone\n{local}\tDocs\n")
    monkeypatch.setenv("UPCLOUD_ROOTS", str(roots))
    serve_remote(rsps, local)
    plan = tmp_path / "plan.tsv"
    assert cli.main(["review", "--out", str(plan)]) == 4
    assert [r[1] for r in read_plan(plan)] == ["Docs/old_same.txt"]


def plan_row(local, name, cloud="Docs", digest=None):
    path = local / name
    return "\t".join([str(path), f"{cloud}/{name}", str(path.stat().st_size),
                      digest or quickxor_file(path), str(int(path.stat().st_mtime))])


def write_plan(tmp_path, *rows):
    plan = tmp_path / "plan.tsv"
    plan.write_text("# local\tonedrive\tsize\tquickxor\tmtime\n" + "\n".join(rows) + "\n")
    return plan


def remote_ok(rsps, local, name):
    rsps.get(item(f"Docs/{name}"), json=file_item(name, (local / name).stat().st_size,
                                                  quickxor_file(local / name)))


def test_offload_dry_run_verifies_but_trashes_nothing(tmp_path, signed_in, rsps, trashed, capsys):
    local = make_local(tmp_path)
    remote_ok(rsps, local, "old_same.txt")
    plan = write_plan(tmp_path, plan_row(local, "old_same.txt"))
    assert cli.main(["offload", str(plan)]) == 0
    assert "Dry run" in capsys.readouterr().out
    assert trashed == [] and (local / "old_same.txt").exists() and not log_path().exists()


def test_offload_apply_trashes_verified_file_and_logs_it(tmp_path, signed_in, rsps, trashed):
    local = make_local(tmp_path)
    remote_ok(rsps, local, "old_same.txt")
    plan = write_plan(tmp_path, plan_row(local, "old_same.txt"))
    assert cli.main(["offload", str(plan), "--apply"]) == 0
    assert trashed == [str(local / "old_same.txt")]
    record = json.loads(log_path().read_text().splitlines()[0])
    assert record["verb"] == "offload" and record["status"] == "trashed" and record["onedrive"] == "Docs/old_same.txt"


@pytest.mark.parametrize("case,reason", [
    ("cloud_gone", "not on OneDrive"),
    ("cloud_hash", "OneDrive copy differs"),
    ("cloud_size", "OneDrive copy differs"),
    ("local_edited", "changed since the plan"),
    ("local_missing", "no longer on this Mac"),
    ("content_differs", "differs from the plan"),
])
def test_offload_refuses_unverified_rows_and_keeps_the_file(tmp_path, signed_in, rsps, trashed, capsys, case, reason):
    local = make_local(tmp_path)
    name = "old_same.txt"
    row = plan_row(local, name)
    real = (local / name).stat().st_size
    if case == "cloud_gone":
        rsps.get(item(f"Docs/{name}"), status=404)
    elif case == "cloud_hash":
        rsps.get(item(f"Docs/{name}"), json=file_item(name, real, "AAAAAAAAAAAAAAAAAAAAAAAAAAA="))
    elif case == "cloud_size":
        rsps.get(item(f"Docs/{name}"), json=file_item(name, real + 1, quickxor_file(local / name)))
    else:
        remote_ok(rsps, local, name)
    if case == "local_edited":
        os.utime(local / name, (time.time(), time.time()))
    elif case == "local_missing":
        (local / name).unlink()
    elif case == "content_differs":
        stat = (local / name).stat()
        (local / name).write_bytes(b"zzzz")  # same size, different bytes
        os.utime(local / name, (stat.st_atime, stat.st_mtime))
    plan = write_plan(tmp_path, row)
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert reason in capsys.readouterr().err
    assert trashed == []
    assert json.loads(log_path().read_text().splitlines()[0])["status"] == "refused"


def test_offload_never_touches_secrets_even_with_a_forged_plan(tmp_path, signed_in, rsps, trashed, capsys):
    local = make_local(tmp_path)
    (local / ".env").write_bytes(b"k")
    rsps.get(item("Docs/.env"), json=file_item(".env", 1, quickxor_file(local / ".env")))
    plan = write_plan(tmp_path, plan_row(local, ".env"), plan_row(local, "tax-2024.pdf"))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert capsys.readouterr().err.count("secret or financial name") == 2
    assert trashed == [] and not [c for c in rsps.calls if "env" in c.request.url]


def test_offload_refuses_a_symlink(tmp_path, signed_in, rsps, trashed, capsys):
    local = make_local(tmp_path)
    (local / "link.txt").symlink_to(local / "old_same.txt")
    plan = write_plan(tmp_path, plan_row(local, "link.txt"))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert "symlink" in capsys.readouterr().err and trashed == []


def test_offload_one_bad_row_does_not_stop_the_good_one(tmp_path, signed_in, rsps, trashed):
    local = make_local(tmp_path)
    rsps.get(item("Docs/hashdiff.txt"), status=404)
    remote_ok(rsps, local, "old_same.txt")
    plan = write_plan(tmp_path, plan_row(local, "hashdiff.txt"), plan_row(local, "old_same.txt"))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert trashed == [str(local / "old_same.txt")]


def test_offload_trash_failure_is_reported_not_raised(tmp_path, signed_in, rsps, monkeypatch, capsys):
    local = make_local(tmp_path)
    remote_ok(rsps, local, "old_same.txt")

    def boom(path):
        raise offload.TrashError("Finder refused")

    monkeypatch.setattr(offload, "trash_path", boom)
    plan = write_plan(tmp_path, plan_row(local, "old_same.txt"))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert "Finder refused" in capsys.readouterr().err
    assert json.loads(log_path().read_text().splitlines()[0])["status"] == "failed"


def test_offload_bad_plan_exits_2_with_the_line(tmp_path, capsys):
    plan = tmp_path / "plan.tsv"
    plan.write_text("only\ttwo\n")
    assert cli.main(["offload", str(plan)]) == 2
    err = capsys.readouterr().err
    assert "line 1" in err and "upcloud review" in err


def test_offload_missing_plan_exits_4(tmp_path, capsys):
    assert cli.main(["offload", str(tmp_path / "nope.tsv")]) == 4


def test_trash_path_uses_the_trash_command(tmp_path, monkeypatch):
    target = tmp_path / "f.txt"
    target.write_bytes(b"x")
    seen = []

    def fake_run(cmd, **kw):
        seen.append(cmd)
        target.unlink()
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(offload.shutil, "which", lambda n, **k: "/usr/bin/trash" if n == "trash" else None)
    monkeypatch.setattr(offload.subprocess, "run", fake_run)
    offload.trash_path(target)
    assert seen == [["/usr/bin/trash", str(target)]]


def test_trash_path_falls_back_to_finder_and_never_hard_deletes(tmp_path, monkeypatch):
    target = tmp_path / "f.txt"
    target.write_bytes(b"x")
    seen = []
    monkeypatch.setattr(offload.shutil, "which", lambda n, **k: "/usr/bin/osascript" if n == "osascript" else None)
    monkeypatch.setattr(offload.subprocess, "run", lambda cmd, **kw: seen.append(cmd))
    with pytest.raises(offload.TrashError):   # the fake did not move the file: treated as not trashed
        offload.trash_path(target)
    assert seen[0][0] == "/usr/bin/osascript" and seen[0][-1] == str(target) and target.exists()


def test_trash_path_without_any_tool_says_what_to_do(tmp_path, monkeypatch):
    monkeypatch.setattr(offload.shutil, "which", lambda n, **k: None)
    with pytest.raises(offload.TrashError) as exc:
        offload.trash_path(tmp_path / "f.txt")
    assert "macOS" in str(exc.value)


@pytest.mark.parametrize("row_fix,reason", [
    (lambda r: r.replace(r.split("\t")[0], "relative/old_same.txt", 1), "not absolute"),
])
def test_offload_refuses_relative_paths(tmp_path, signed_in, rsps, trashed, capsys, row_fix, reason):
    local = make_local(tmp_path)
    plan = write_plan(tmp_path, row_fix(plan_row(local, "old_same.txt")))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert reason in capsys.readouterr().err and trashed == []


def test_offload_refuses_files_inside_a_synced_onedrive_folder(tmp_path, signed_in, rsps, trashed, capsys):
    synced = tmp_path / "OneDrive-Personal"
    synced.mkdir()
    (synced / "f.txt").write_bytes(b"abcd")
    plan = write_plan(tmp_path, plan_row(synced, "f.txt"))
    assert cli.main(["offload", str(plan), "--apply"]) == 5
    assert "synced OneDrive" in capsys.readouterr().err and trashed == []


def test_move_log_failure_warns_but_does_not_abort(monkeypatch, capsys):
    from upcloud import movelog
    monkeypatch.setenv("UPCLOUD_MOVE_LOG", "/proc/definitely/not/writable/moves.jsonl")
    movelog.log_move("mv", src="a", status="ok")
    assert "could not write the move log" in capsys.readouterr().err
