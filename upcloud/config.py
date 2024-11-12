import os, json, logging, requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from jwt import decode, InvalidTokenError

load_dotenv()

class Config:
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('AZURE_VALUE')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080')
    AUTHORITY_URL = os.getenv('AUTHORITY_URL', 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize')
    TOKEN_URL = os.getenv('TOKEN_URL', 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token')
    SCOPES = os.getenv('SCOPES', 'https://graph.microsoft.com/.default').split()
    CACHED_TOKEN_PATH = os.getenv('CACHED_TOKEN_PATH', 'secret.json')


def get_access_token():
    try:
        with open(Config.CACHED_TOKEN_PATH) as f:
            t = json.load(f)
            if t.get('access_token') and is_valid_jwt(t['access_token']):
                return t['access_token']
            elif t.get('refresh_token'):
                return refresh_access_token(t['refresh_token'])
            else:
                raise_exception()
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Token error: {e}")
        auth_url = f"{Config.AUTHORITY_URL}?client_id={Config.CLIENT_ID}&response_type=code&redirect_uri={Config.REDIRECT_URI}&response_mode=query&scope={' '.join(Config.SCOPES)}"
        print(f"Authorize: {auth_url}")
        code = input("Code: ")
        token = requests.post(Config.TOKEN_URL, data={
            'client_id': Config.CLIENT_ID, 'client_secret': Config.CLIENT_SECRET,
            'grant_type': 'authorization_code', 'code': code,
            'redirect_uri': Config.REDIRECT_URI, 'scope': ' '.join(Config.SCOPES)
        }, auth=HTTPBasicAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)).json()
        token['auth_code'] = code
        with open(Config.CACHED_TOKEN_PATH, 'w') as f:
            json.dump(token, f)
        return token['access_token']


def refresh_access_token(rt):
    token = requests.post(Config.TOKEN_URL, data={
        'client_id': Config.CLIENT_ID, 'client_secret': Config.CLIENT_SECRET,
        'grant_type': 'refresh_token', 'refresh_token': rt,
        'scope': ' '.join(Config.SCOPES)
    }, auth=HTTPBasicAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)).json()
    token['refresh_token'] = rt
    with open(Config.CACHED_TOKEN_PATH, 'w') as f:
        json.dump(token, f)
    return token['access_token']


def raise_exception():
    raise ValueError("Invalid access token format")


def is_valid_jwt(token):
    try:
        decode(token, options={"verify_signature": False})
        return True
    except InvalidTokenError:
        return False
