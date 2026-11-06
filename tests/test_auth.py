import json
import os
import stat
import time

import jwt
import pytest

from upcloud import config
from upcloud.config import AuthRequired, Config

TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"


def write_cache(data):
    with open(Config.CACHED_TOKEN_PATH, "w") as f:
        json.dump(data, f)


def read_cache():
    with open(Config.CACHED_TOKEN_PATH) as f:
        return json.load(f)


def test_fresh_cached_token_is_returned_without_network(rsps):
    write_cache({"access_token": "opaque-a", "refresh_token": "r1", "expires_in": 3600,
                 "obtained_at": int(time.time())})
    assert config.get_access_token(interactive=False) == "opaque-a"
    assert len(rsps.calls) == 0


def test_expired_token_by_obtained_at_is_refreshed(rsps):
    write_cache({"access_token": "old", "refresh_token": "r1", "expires_in": 3600,
                 "obtained_at": int(time.time()) - 3500})  # inside the 5 min margin
    rsps.post(TOKEN_URL, json={"access_token": "new", "expires_in": 3600, "token_type": "Bearer"})
    assert config.get_access_token(interactive=False) == "new"
    body = rsps.calls[0].request.body
    assert "grant_type=refresh_token" in body and "offline_access" in body
    saved = read_cache()
    assert saved["access_token"] == "new"
    assert saved["refresh_token"] == "r1"  # kept when the server omits it
    assert abs(saved["obtained_at"] - time.time()) < 5


def test_expired_jwt_without_obtained_at_is_refreshed(rsps):
    expired = jwt.encode({"exp": int(time.time()) - 60}, "k", algorithm="HS256")
    write_cache({"access_token": expired, "refresh_token": "r1", "expires_in": 3600})
    rsps.post(TOKEN_URL, json={"access_token": "new", "refresh_token": "r2", "expires_in": 3600})
    assert config.get_access_token(interactive=False) == "new"
    assert read_cache()["refresh_token"] == "r2"


def test_opaque_token_without_obtained_at_is_treated_as_stale(rsps):
    write_cache({"access_token": "EwB-opaque", "refresh_token": "r1", "expires_in": 3600})
    rsps.post(TOKEN_URL, json={"access_token": "new", "expires_in": 3600})
    assert config.get_access_token(interactive=False) == "new"


def test_token_cache_is_written_mode_0600(rsps):
    write_cache({"access_token": "old", "refresh_token": "r1", "expires_in": 1, "obtained_at": 0})
    os.chmod(Config.CACHED_TOKEN_PATH, 0o644)
    rsps.post(TOKEN_URL, json={"access_token": "new", "expires_in": 3600})
    config.get_access_token(interactive=False)
    assert stat.S_IMODE(os.stat(Config.CACHED_TOKEN_PATH).st_mode) == 0o600


def test_non_interactive_without_cache_raises_auth_required():
    with pytest.raises(AuthRequired):
        config.get_access_token(interactive=False)


def test_failed_refresh_non_interactive_raises_auth_required(rsps):
    write_cache({"access_token": "old", "refresh_token": "r1", "expires_in": 1, "obtained_at": 0})
    rsps.post(TOKEN_URL, status=400, json={"error": "invalid_grant", "error_description": "expired"})
    with pytest.raises(AuthRequired):
        config.get_access_token(interactive=False)


def test_scopes_always_include_offline_access(monkeypatch):
    monkeypatch.setenv("SCOPES", "https://graph.microsoft.com/.default")
    Config.reload()
    assert "offline_access" in Config.SCOPES


def test_azure_redirect_uri_is_accepted(monkeypatch):
    monkeypatch.setenv("AZURE_REDIRECT_URI", "http://localhost:8765")
    Config.reload()
    assert Config.REDIRECT_URI == "http://localhost:8765"


def test_relative_token_path_resolves_against_env_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("CACHED_TOKEN_PATH", "token_cache.json")
    monkeypatch.setattr(config, "ENV_DIR", str(tmp_path))
    Config.reload()
    assert Config.CACHED_TOKEN_PATH == str(tmp_path / "token_cache.json")
