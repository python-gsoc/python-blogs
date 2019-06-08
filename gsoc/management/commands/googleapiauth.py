import pickle
import os

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from django.core.management import BaseCommand

from gsoc.settings import GOOGLE_API_SCOPES, GOOGLE_API_CLIENT_CONFIG, BASE_DIR


class Command(BaseCommand):
    help = 'Generates the api token pickle for authenticating Google API.'
    requires_system_checks = False   # for debugging

    def handle(self, *args, **options):
        if os.path.exists(os.path.join(BASE_DIR, 'google_api_token.pickle')):
            os.remove(os.path.join(BASE_DIR, 'google_api_token.pickle'))

        flow = InstalledAppFlow.from_client_config(
            GOOGLE_API_CLIENT_CONFIG, GOOGLE_API_SCOPES
        )
        creds = flow.run_console()

        with open(os.path.join(BASE_DIR, 'google_api_token.pickle'), 'wb') as token:
            pickle.dump(creds, token)
