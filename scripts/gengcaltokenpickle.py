import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Needs credentials.json downloadable from
# https://developers.google.com/calendar/quickstart/python
# in the same directory as the script to run
# and then place the pickle file generated in the root directory
# of the application (the script automatically does that although
# needs to copied to the server)

creds = None
if os.path.exists('../gcal_api_token.pickle'):
    with open('../gcal_api_token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.Refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server()

    with open('../gcal_api_token.pickle', 'wb') as token:
        pickle.dump(creds, token)
