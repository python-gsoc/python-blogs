import os

from gsoc.settings import BASE_DIR

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from django.core.management.base import BaseCommand, CommandError

SCOPES = ['https://www.googleapis.com/auth/calendar']


class Command(BaseCommand):
    help = "Google OAuth"
if os.path.exists(os.path.join(BASE_DIR, 'token.json')):
    creds = Credentials.from_authorized_user_file(
        os.path.join(BASE_DIR, 'token.json'),
        SCOPES
    )
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:

    def handle(self, *args, **kwargs):
        flow = Flow.from_client_secrets_file(
            os.path.join(BASE_DIR, 'credentials.json'),
            SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )

        auth_url, _ = flow.authorization_url(prompt='consent')

        print('Please go to this URL: {}'.format(auth_url))

        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)

        creds = flow.credentials

        with open(os.path.join(BASE_DIR, 'token.json'), 'w') as token:
            token.write(creds.to_json())
