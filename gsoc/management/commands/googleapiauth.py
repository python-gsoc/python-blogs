from google_auth_oauthlib.flow import InstalledAppFlow
import os.path

from google.auth.transport.requests import Request

from django.core.management import BaseCommand

from gsoc.settings import GOOGLE_API_SCOPES, GOOGLE_API_CLIENT_CONFIG


class Command(BaseCommand):
    help = 'Generates the api token pickle for authenticating Google API.'
    requires_system_checks = False   # for debugging

    def handle(self, *args, **options):
        creds = None
        if os.path.exists('gcal_api_token.pickle'):
            with open('gcal_api_token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.Refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    GOOGLE_API_CLIENT_CONFIG, GOOGLE_API_SCOPES
                )
                creds = flow.run_console()

            with open('gcal_api_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
