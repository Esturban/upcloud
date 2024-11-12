import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests
import json
import logging
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
        with open(Config.CACHED_TOKEN_PATH, 'r') as f:
            tokens = json.load(f)
            access_token = tokens.get('access_token')
            auth_code = tokens.get('auth_code')
            if access_token and is_valid_jwt(access_token):
                return access_token
            else:
                raise ValueError("Invalid access token format")
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Token retrieval error: {e}")
        auth_url = (
            f"{Config.AUTHORITY_URL}?client_id={Config.CLIENT_ID}&response_type=code&redirect_uri={Config.REDIRECT_URI}"
            f"&response_mode=query&scope={' '.join(Config.SCOPES)}"
        )
        print(f"Go to the following URL to authorize the application: {auth_url}")
        auth_code = input("Enter the authorization code: ")

        token_data = {
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': Config.REDIRECT_URI,
            'scope': ' '.join(Config.SCOPES)
        }
        response = requests.post(Config.TOKEN_URL, data=token_data, auth=HTTPBasicAuth(Config.CLIENT_ID, Config.CLIENT_SECRET))
        response.raise_for_status()
        tokens = response.json()
        tokens['auth_code'] = auth_code
        with open(Config.CACHED_TOKEN_PATH, 'w') as f:
            json.dump(tokens, f)
        return tokens['access_token']


def is_valid_jwt(token):
    try:
        decode(token, options={"verify_signature": False})
        return True
    except InvalidTokenError:
        return False
