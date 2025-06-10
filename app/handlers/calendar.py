#GENAI_ASSISTANT/app/handlers/calendar
 
import datetime
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def clean_summary(text: str) -> str:
    """
    Cleans the input text by removing common reminder phrases.
    """
    text = text.lower().strip()

    prefixes = [
        "set a reminder to",
        "set a reminder for",
        "remind me to",
        "remind me about",
        "create an event to",
        "make a calendar event to"
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            cleaned = text[len(prefix):].strip()
            return cleaned[0].upper() + cleaned[1:] 

    return text[0].upper() + text[1:] if text else text


def get_calendar_service():
    """
    Authenticates and returns a Google Calendar API service object.
    Saves a token to avoid repeated login.
    """
    creds = None
    token_path = os.path.join("app", "config", "token.pickle")
    creds_path = os.path.join("app", "config", "credentials.json")

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=8765)  # Fixed port

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def handle_calendar(command: str) -> str:
    """
    Creates a calendar event based on the command string.
    Currently uses fixed time slots (1 hour from now).
    """
    summary = clean_summary(command)

    start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat() + 'Z'
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).isoformat() + 'Z'

    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Calendar event created: {created_event.get('htmlLink')}"
