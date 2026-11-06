import json

from conftest import file_item, folder_item
from upcloud import cli
from upcloud.movelog import log_path
from upcloud.onedrive_client import OneDriveClient

DRIVE = "https://graph.microsoft.com/v1.0/me/drive"
ROOT = DRIVE + "/root"


def item(path):
    return f"{ROOT}:/{path}" if path else ROOT


def children(path):
    return f"{ROOT}:/{path}:/children"


def logged():
    return [json.loads(line) for line in log_path().read_text().splitlines()]


def patches(rsps):
    return [c for c in rsps.calls if c.request.method == "PATCH"]


def test_client_move_item_patches_parent_and_name(rsps):
    rsps.patch(f"{DRIVE}/items/F1", json={"id": "F1"})
    OneDriveClient("t").move_item("F1", "P9", "new.txt")
    body = json.loads(patches(rsps)[0].request.body)
    assert body == {"parentReference": {"id": "P9"}, "name": "new.txt"}


def test_mv_dry_run_changes_nothing(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a/f.txt"), json=file_item("f.txt", 1, item_id="F1"))
    rsps.get(item("b/f.txt"), status=404)
    rsps.get(item("b"), json=folder_item("b", "B1"))
    assert cli.main(["mv", "a/f.txt", "b/f.txt"]) == 0
    assert "a/f.txt -> b/f.txt" in capsys.readouterr().out
    assert not patches(rsps) and not log_path().exists()


def test_mv_apply_moves_by_id_and_logs(monkeypatch, rsps):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a/f.txt"), json=file_item("f.txt", 1, item_id="F1"))
    rsps.get(item("b/g.txt"), status=404)
    rsps.get(item("b"), json=folder_item("b", "B1"))
    rsps.patch(f"{DRIVE}/items/F1", json={"id": "F1"})
    assert cli.main(["mv", "a/f.txt", "b/g.txt", "--apply"]) == 0
    assert json.loads(patches(rsps)[0].request.body) == {"parentReference": {"id": "B1"}, "name": "g.txt"}
    assert logged()[0]["verb"] == "mv" and logged()[0]["status"] == "ok"


def test_mv_refuses_to_overwrite(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a/f.txt"), json=file_item("f.txt", 1, item_id="F1"))
    rsps.get(item("b/f.txt"), json=file_item("f.txt", 2, item_id="F2"))
    assert cli.main(["mv", "a/f.txt", "b/f.txt", "--apply"]) == 1
    assert "already exists" in capsys.readouterr().err and not patches(rsps)


def test_mv_missing_source_exits_4(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("nope"), status=404)
    assert cli.main(["mv", "nope", "x"]) == 4
    assert "upcloud ls" in capsys.readouterr().err


def test_mv_trailing_slash_moves_into_folder_keeping_the_name(monkeypatch, rsps):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a/f.txt"), json=file_item("f.txt", 1, item_id="F1"))
    rsps.get(item("b/f.txt"), status=404)
    rsps.get(item("b"), json=folder_item("b", "B1"))
    rsps.patch(f"{DRIVE}/items/F1", json={"id": "F1"})
    assert cli.main(["mv", "a/f.txt", "b/", "--apply"]) == 0
    assert json.loads(patches(rsps)[0].request.body)["name"] == "f.txt"


def test_mv_creates_missing_parents_on_apply_only(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a/f.txt"), json=file_item("f.txt", 1, item_id="F1"))
    rsps.get(item("n/m/f.txt"), status=404)
    rsps.get(item("n/m"), status=404)
    rsps.get(item("n"), status=404)
    assert cli.main(["mv", "a/f.txt", "n/m/f.txt"]) == 0
    assert "would create folder n/m" in capsys.readouterr().out
    assert not [c for c in rsps.calls if c.request.method in ("POST", "PATCH")]
    rsps.post(f"{ROOT}/children", status=201, json=folder_item("n", "N1"))
    rsps.post(children("n"), status=201, json=folder_item("m", "M1"))
    rsps.replace("GET", item("n/m"), json=folder_item("m", "M1"))
    rsps.patch(f"{DRIVE}/items/F1", json={"id": "F1"})
    assert cli.main(["mv", "a/f.txt", "n/m/f.txt", "--apply"]) == 0
    assert json.loads(patches(rsps)[0].request.body)["parentReference"] == {"id": "M1"}


def test_mv_refuses_to_move_a_folder_into_itself(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("a"), json=folder_item("a", "A1"))
    assert cli.main(["mv", "a", "a/sub/a", "--apply"]) == 1
    assert "into itself" in capsys.readouterr().err


# sort-by-year

def photo(name, taken=None, created=None, item_id=None):
    entry = file_item(name, 5, item_id=item_id)
    if taken:
        entry["photo"] = {"takenDateTime": taken}
    if created:
        entry["fileSystemInfo"] = {"createdDateTime": created}
    return entry


def listing(rsps, loose, years=("2019", "2020"), existing=None):
    existing = existing or {}
    rsps.get(children("Pics"), json={"value": [folder_item(y, f"Y{y}") for y in years] + loose})
    for y in years:
        rsps.get(children(f"Pics/{y}"), json={"value": existing.get(y, [])})


def test_sort_plans_by_photo_taken_date_then_created_date(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    listing(rsps, [photo("a.jpg", taken="2019-05-01T10:00:00Z", created="2024-01-01T00:00:00Z", item_id="A"),
                   photo("b.pdf", created="2020-03-03T00:00:00Z", item_id="B")])
    assert cli.main(["sort-by-year", "Pics"]) == 0
    out = capsys.readouterr().out
    assert "a.jpg -> 2019/" in out and "b.pdf -> 2020/" in out and "Dry run" in out
    assert not patches(rsps)


def test_sort_apply_moves_into_existing_year_folders_and_logs(monkeypatch, rsps):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    listing(rsps, [photo("a.jpg", taken="2019-05-01T10:00:00Z", item_id="A")])
    rsps.patch(f"{DRIVE}/items/A", json={"id": "A"})
    assert cli.main(["sort-by-year", "Pics", "--apply"]) == 0
    assert json.loads(patches(rsps)[0].request.body) == {"parentReference": {"id": "Y2019"}, "name": "a.jpg"}
    assert logged()[0]["verb"] == "sort-by-year" and logged()[0]["dst"] == "Pics/2019/a.jpg"


def test_sort_never_creates_a_year_folder(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    listing(rsps, [photo("a.jpg", taken="2015-01-01T00:00:00Z")])
    assert cli.main(["sort-by-year", "Pics", "--apply"]) == 0
    assert "no 2015/ folder" in capsys.readouterr().out
    assert not [c for c in rsps.calls if c.request.method in ("POST", "PATCH")]


def test_sort_skips_name_clashes_and_undated_files(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    listing(rsps, [photo("a.jpg", taken="2019-05-01T10:00:00Z"), photo("nodate.bin")],
            existing={"2019": [file_item("a.jpg", 1)]})
    assert cli.main(["sort-by-year", "Pics", "--apply"]) == 0
    out = capsys.readouterr().out
    assert "already in 2019/" in out and "no date" in out and not patches(rsps)


def test_sort_leaves_subfolders_and_other_folders_alone(monkeypatch, rsps):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(children("Pics"), json={"value": [folder_item("2019", "Y2019"), folder_item("trips", "T1")]})
    assert cli.main(["sort-by-year", "Pics", "--apply"]) == 0
    assert not patches(rsps)


def test_sort_one_failed_move_exits_5_and_continues(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    listing(rsps, [photo("a.jpg", taken="2019-01-01T00:00:00Z", item_id="A"),
                   photo("b.jpg", taken="2019-01-01T00:00:00Z", item_id="B")])
    rsps.patch(f"{DRIVE}/items/A", status=409)
    rsps.patch(f"{DRIVE}/items/B", json={"id": "B"})
    assert cli.main(["sort-by-year", "Pics", "--apply"]) == 5
    assert "failed" in capsys.readouterr().err
    assert {r["status"] for r in logged()} == {"ok", "failed"}


def test_mv_empty_source_is_refused_before_touching_the_drive(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    assert cli.main(["mv", "/", "x"]) == 1
    assert not rsps.calls


def test_mv_into_itself_is_caught_case_insensitively(monkeypatch, rsps, capsys):
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get(item("Docs"), json=folder_item("Docs", "D1"))
    assert cli.main(["mv", "Docs", "docs/x/Docs"]) == 1
    assert "into itself" in capsys.readouterr().err
