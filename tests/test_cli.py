import subprocess
import sys

import pytest

from conftest import ROOT, file_item, folder_item
from upcloud import cli, config
from upcloud.config import Config


def test_python_dash_m_help_lists_commands():
    out = subprocess.run([sys.executable, "-m", "upcloud", "--help"], cwd=ROOT, capture_output=True,
                         text=True, env={"UPCLOUD_NO_DOTENV": "1", "PATH": ""})
    assert out.returncode == 0
    assert "login" in out.stdout


def test_no_args_prints_overview(capsys):
    assert cli.main([]) == 0
    assert "login" in capsys.readouterr().out


def test_login_without_client_id_exits_3_with_fix(monkeypatch, capsys):
    monkeypatch.delenv("CLIENT_ID")
    Config.reload()
    assert cli.main(["login"]) == 3
    assert "CLIENT_ID" in capsys.readouterr().err


def test_authorize_url_has_state_offline_access_and_redirect(monkeypatch):
    monkeypatch.setenv("AZURE_REDIRECT_URI", "http://localhost:8765")
    Config.reload()
    url = config.build_authorize_url("st4te")
    assert "state=st4te" in url and "offline_access" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8765" in url


GRAPH_ROOT = "https://graph.microsoft.com/v1.0/me/drive/root"


@pytest.fixture
def signed_in(monkeypatch):
    from upcloud.onedrive_client import OneDriveClient
    monkeypatch.setattr(cli, "make_client", lambda: OneDriveClient("test-token"))


def test_ls_follows_pages_and_marks_folders(signed_in, rsps, capsys):
    first = GRAPH_ROOT + ":/D:/children"
    nxt = "https://graph.microsoft.com/v1.0/me/drive/items/D/children?$skiptoken=abc"
    rsps.get(first, json={"value": [folder_item("sub", size=2048)], "@odata.nextLink": nxt})
    rsps.get(nxt, json={"value": [file_item("a.csv", 5)]})
    assert cli.main(["ls", "D"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].endswith("sub/") and "2.0 KB" in out[0]
    assert out[1].endswith("a.csv") and "5 B" in out[1]


def test_ls_missing_folder_exits_4(signed_in, rsps, capsys):
    rsps.get(GRAPH_ROOT + ":/nope:/children", status=404)
    assert cli.main(["ls", "nope"]) == 4
    assert "upcloud ls" in capsys.readouterr().err


def test_ls_without_sign_in_exits_3(capsys):
    assert cli.main(["ls"]) == 3
    assert "upcloud login" in capsys.readouterr().err
