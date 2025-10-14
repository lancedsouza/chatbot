import datetime
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    token_path = 'token.pkl'
    creds_path = os.getenv("GOOGLE_CREDS_PATH", "google_creds/credentials.json")

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def create_event(name, date_str, time_str, purpose):
    service = get_calendar_service()

    # Parse input strings
    try:
        start = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except Exception as e:
        return f"❌ Date/time format error: {e}"

    end = start + datetime.timedelta(hours=1)  # Default 1 hour event

    event = {
        'summary': purpose,
        'description': f"Appointment with {name}",
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'UTC',
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"📅 Event created: {created_event.get('htmlLink')}"
