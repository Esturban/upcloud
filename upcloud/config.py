"""Auth for a personal Microsoft account (consumers authority), auth-code flow.

Token cache keeps the original shape (access_token, refresh_token, expires_in, ...)
plus obtained_at, and is written with mode 0600. Secrets never reach stdout.
"""
import json
import os
import tempfile
import threading
import time
import webbrowser
from urllib.parse import urlencode

import requests
from jwt import InvalidTokenError, decode

DEFAULT_SCOPES = "https://graph.microsoft.com/.default offline_access"
REFRESH_MARGIN_SECONDS = 300
HTTP_TIMEOUT_SECONDS = 30
ENV_DIR = None  # directory of the loaded .env; relative cache paths resolve against it


class AuthRequired(Exception):
    """No usable token and no interactive sign-in allowed."""


def load_env() -> None:
    """Load .env: UPCLOUD_ENV_FILE, else this repo's .env, else one found from the cwd up.

    Skipped entirely when UPCLOUD_NO_DOTENV is set (tests).
    """
    global ENV_DIR
    if os.getenv("UPCLOUD_NO_DOTENV"):
        return
    from dotenv import find_dotenv, load_dotenv
    repo_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    path = os.getenv("UPCLOUD_ENV_FILE") or (repo_env if os.path.exists(repo_env) else "")
    path = path or find_dotenv(usecwd=True)
    if path:
        load_dotenv(path)
        ENV_DIR = os.path.dirname(path)
    Config.reload()


def _resolve(path: str) -> str:
    if os.path.isabs(path) or not ENV_DIR:
        return path
    return os.path.join(ENV_DIR, path)


class Config:
    @classmethod
    def reload(cls) -> None:
        cls.CLIENT_ID = os.getenv("CLIENT_ID")
        cls.CLIENT_SECRET = os.getenv("AZURE_VALUE")
        cls.REDIRECT_URI = (os.getenv("REDIRECT_URI") or os.getenv("AZURE_REDIRECT_URI")
                            or "http://localhost:8080")
        cls.AUTHORITY_URL = os.getenv(
            "AUTHORITY_URL", "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize")
        cls.TOKEN_URL = os.getenv(
            "TOKEN_URL", "https://login.microsoftonline.com/consumers/oauth2/v2.0/token")
        scopes = os.getenv("SCOPES", DEFAULT_SCOPES).split()
        cls.SCOPES = scopes if "offline_access" in scopes else scopes + ["offline_access"]
        cls.CACHED_TOKEN_PATH = _resolve(os.getenv("CACHED_TOKEN_PATH", "secret.json"))


Config.reload()


# ---- token cache ---------------------------------------------------------------

def load_token():
    try:
        with open(Config.CACHED_TOKEN_PATH) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (FileNotFoundError, ValueError):
        return None


def save_token(token: dict, previous: dict = None) -> dict:
    """Persist a token response with obtained_at, keeping the old refresh_token if omitted."""
    merged = dict(token)
    if previous and previous.get("refresh_token") and not merged.get("refresh_token"):
        merged["refresh_token"] = previous["refresh_token"]
    merged["obtained_at"] = int(time.time())
    path = Config.CACHED_TOKEN_PATH
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".token-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(merged, f)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    os.chmod(path, 0o600)
    return merged


def _jwt_exp(access_token):
    try:
        return decode(access_token, options={"verify_signature": False}).get("exp")
    except InvalidTokenError:
        return None


def token_is_fresh(token: dict, now: float = None) -> bool:
    """True if the access token is valid for at least REFRESH_MARGIN_SECONDS more."""
    now = time.time() if now is None else now
    if not token or not token.get("access_token"):
        return False
    if "obtained_at" in token and "expires_in" in token:
        return now < float(token["obtained_at"]) + float(token["expires_in"]) - REFRESH_MARGIN_SECONDS
    exp = _jwt_exp(token["access_token"])  # consumer tokens are often opaque: None
    return bool(exp) and now < float(exp) - REFRESH_MARGIN_SECONDS


def is_valid_jwt(token):
    """Kept for compatibility: structural check only, says nothing about expiry."""
    try:
        decode(token, options={"verify_signature": False})
        return True
    except InvalidTokenError:
        return False


# ---- token endpoint ------------------------------------------------------------

def _token_request(data: dict) -> dict:
    data = {"client_id": Config.CLIENT_ID, "scope": " ".join(Config.SCOPES), **data}
    if Config.CLIENT_SECRET:
        data["client_secret"] = Config.CLIENT_SECRET
    resp = requests.post(Config.TOKEN_URL, data=data, timeout=HTTP_TIMEOUT_SECONDS,
                         headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if resp.status_code >= 400 or "error" in body or "access_token" not in body:
        reason = body.get("error_description") or body.get("error") or f"HTTP {resp.status_code}"
        raise AuthRequired(f"Microsoft sign-in was refused: {reason.splitlines()[0]}")
    return body


def refresh_access_token(refresh_token, interactive=True):
    try:
        token = _token_request({"grant_type": "refresh_token", "refresh_token": refresh_token,
                                "redirect_uri": Config.REDIRECT_URI})
    except (AuthRequired, requests.RequestException):
        if interactive:
            return get_new_token()
        raise AuthRequired("The cached sign-in has expired and could not be refreshed.")
    return save_token(token, previous=load_token())["access_token"]


def get_access_token(interactive=True):
    token = load_token()
    if token_is_fresh(token):
        return token["access_token"]
    if token and token.get("refresh_token"):
        return refresh_access_token(token["refresh_token"], interactive=interactive)
    if interactive:
        return get_new_token()
    raise AuthRequired(f"No usable sign-in found at {Config.CACHED_TOKEN_PATH}.")


# ---- interactive sign-in -------------------------------------------------------

def get_new_token():
    from .server import run_server  # fastapi/uvicorn load only for sign-in

    event = threading.Event()
    app_instance, thread = run_server(event)
    query = urlencode({"client_id": Config.CLIENT_ID, "response_type": "code",
                       "redirect_uri": Config.REDIRECT_URI, "response_mode": "query",
                       "scope": " ".join(Config.SCOPES)})
    webbrowser.open(f"{Config.AUTHORITY_URL}?{query}")
    event.wait()
    code = app_instance.state.auth_code
    app_instance.state.server.force_exit = True
    thread.join(timeout=1)
    token = _token_request({"grant_type": "authorization_code", "code": code,
                            "redirect_uri": Config.REDIRECT_URI})
    return save_token(token)["access_token"]
