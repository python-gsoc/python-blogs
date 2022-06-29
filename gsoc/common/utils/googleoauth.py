import os

from gsoc.settings import BASE_DIR

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']


def getCreds():
    creds = None
    if os.path.exists(os.path.join(BASE_DIR, 'token.json')):
        creds = Credentials.from_authorized_user_file(
            os.path.join(BASE_DIR, 'token.json'),
            SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(BASE_DIR, 'credentials.json'),
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(os.path.join(BASE_DIR, 'token.json'), 'w') as token:
            token.write(creds.to_json())
    return creds
