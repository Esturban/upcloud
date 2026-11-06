import pytest

from upcloud import cli
from upcloud.roots import RootsError, load_roots, resolve


def write_roots(tmp_path, monkeypatch, text):
    path = tmp_path / "roots.tsv"
    path.write_text(text)
    monkeypatch.setenv("UPCLOUD_ROOTS", str(path))
    return path


def test_missing_roots_file_is_an_empty_list():
    assert load_roots() == []


def test_load_skips_comments_and_blank_lines_and_expands_home(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, "# my roots\n\n~/Pictures\tPictures\n/data/docs\t/Documents/\n")
    roots = load_roots()
    assert [r.onedrive for r in roots] == ["Pictures", "Documents"]
    assert roots[0].local.is_absolute() and roots[1].local.as_posix() == "/data/docs"


def test_malformed_line_names_the_line_and_the_fix(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, "/a\tA\nnot-tab-separated\n")
    with pytest.raises(RootsError) as exc:
        load_roots()
    assert "line 2" in str(exc.value) and "TAB" in str(exc.value)


def test_relative_local_dir_is_rejected(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, "photos\tPhotos\n")
    with pytest.raises(RootsError):
        load_roots()


def test_resolve_maps_a_subfolder_to_the_matching_cloud_subfolder(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/pics\tPictures\n{tmp_path}\tAll\n")
    assert resolve(tmp_path / "pics" / "2019" / "trip") == ("Pictures/2019/trip")
    assert resolve(tmp_path / "pics") == "Pictures"
    assert resolve(tmp_path / "other") == "All/other"


def test_resolve_returns_none_outside_every_root(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/pics\tPictures\n")
    assert resolve(tmp_path / "elsewhere") is None


def test_mirror_with_no_args_mirrors_every_root(tmp_path, monkeypatch, rsps, capsys):
    from upcloud.onedrive_client import OneDriveClient
    (tmp_path / "a").mkdir(); (tmp_path / "b").mkdir()
    (tmp_path / "a" / "x.txt").write_bytes(b"x")
    (tmp_path / "b" / "y.txt").write_bytes(b"y")
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/a\tA\n{tmp_path}/b\tB\n")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/A", status=404)
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/B", status=404)
    assert cli.main(["mirror"]) == 0
    out = capsys.readouterr().out
    assert "upload   x.txt" in out and "upload   y.txt" in out and "-> OneDrive:A" in out and "-> OneDrive:B" in out
    assert all(c.request.method == "GET" for c in rsps.calls)


def test_mirror_path_resolves_its_cloud_folder_from_the_roots_file(tmp_path, monkeypatch, rsps, capsys):
    from upcloud.onedrive_client import OneDriveClient
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.txt").write_bytes(b"x")
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/a\tA\n")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/A", status=404)
    assert cli.main(["mirror", str(tmp_path / "a")]) == 0
    assert "-> OneDrive:A" in capsys.readouterr().out


def test_mirror_path_outside_roots_without_env_target_exits_2(tmp_path, capsys):
    assert cli.main(["mirror", str(tmp_path)]) == 2
    assert "roots.tsv" in capsys.readouterr().err


def test_mirror_missing_root_folder_is_reported_and_the_rest_still_run(tmp_path, monkeypatch, rsps, capsys):
    from upcloud.onedrive_client import OneDriveClient
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "y.txt").write_bytes(b"y")
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/gone\tG\n{tmp_path}/b\tB\n")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/B", status=404)
    assert cli.main(["mirror"]) == 4
    captured = capsys.readouterr()
    assert "gone" in captured.err and "upload   y.txt" in captured.out


def test_resolve_ignores_case_on_a_case_insensitive_mac(tmp_path, monkeypatch):
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/Pictures\tPictures\n")
    assert resolve(str(tmp_path / "pictures" / "x")) == "Pictures/x"


def test_malformed_roots_file_is_a_clean_usage_error(tmp_path, monkeypatch, capsys):
    write_roots(tmp_path, monkeypatch, "oops\n")
    assert cli.main(["mirror"]) == 2
    assert "TAB" in capsys.readouterr().err


def test_mirror_of_a_single_file_uses_its_folders_cloud_path(tmp_path, monkeypatch, rsps, capsys):
    from upcloud.onedrive_client import OneDriveClient
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.txt").write_bytes(b"x")
    write_roots(tmp_path, monkeypatch, f"{tmp_path}/a\tA\n")
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("t"))
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/A", status=404)
    assert cli.main(["mirror", str(tmp_path / "a" / "x.txt")]) == 0
    assert "-> OneDrive:A:" in capsys.readouterr().out


def test_paths_with_hash_and_percent_are_url_encoded(rsps):
    from upcloud.onedrive_client import OneDriveClient
    rsps.get("https://graph.microsoft.com/v1.0/me/drive/root:/a%23b/100%25", json={"id": "1"})
    assert OneDriveClient("t").get_item("a#b/100%")["id"] == "1"
