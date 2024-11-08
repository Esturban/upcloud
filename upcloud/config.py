import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests
load_dotenv()
class Config:
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('AZURE_VALUE')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080')
    AUTHORITY_URL = os.getenv('AUTHORITY_URL', 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize')
    TOKEN_URL = os.getenv('TOKEN_URL', 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token')
    SCOPES = os.getenv('SCOPES', 'https://graph.microsoft.com/.default').split()


def get_access_token():
    auth_url = f"{Config.AUTHORITY_URL}?client_id={Config.CLIENT_ID}&response_type=code&redirect_uri={Config.REDIRECT_URI}&response_mode=query&scope={' '.join(Config.SCOPES)}"
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
    return response.json()['access_token']