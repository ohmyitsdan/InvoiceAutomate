import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/gmail.labels']

def googleAPIcreds():
    creds = None
    # The file mailtoken.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(os.getcwd(),'credentials','token.pickle')):
        with open(os.path.join(os.getcwd(),'credentials','token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(os.getcwd(),'credentials','credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join('credentials','token.pickle'), 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service

if __name__ == "__main__":
    service = googleAPIcreds()
    results = service.users().messages().list(userId='me',includeSpamTrash=False, maxResults=5).execute()
    messages = results.get('messages', [])
    print(messages)