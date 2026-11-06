import subprocess
import sys

from conftest import ROOT
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
