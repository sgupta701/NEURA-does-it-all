import datetime
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    """Authenticate and return a Google Calendar API service instance."""
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
            creds = flow.run_local_server(port=8765)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def handle_calendar(command: str) -> str:
    """
    Demo version:
    - Removes common prefixes
    - Cleans up the summary to just keywords (like "meeting scheduled")
    - Creates a calendar event on 12 Oct 2025, 5 PM
    """
    # Remove common prefixes
    prefixes = [
        "set a reminder to",
        "set a reminder for",
        "remind me to",
        "remind me about",
        "create an event to",
        "make a calendar event to"
    ]
    summary = command.strip()
    for prefix in prefixes:
        if summary.lower().startswith(prefix):
            summary = summary[len(prefix):].strip()
            break

    # Remove any date mentions using regex
    summary = re.sub(r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', '', summary, flags=re.I)
    summary = re.sub(r'\bat\s+\d{1,2}(:\d{2})?\s*(am|pm)?\b', '', summary, flags=re.I)

    # Remove extra spaces and capitalize
    summary = summary.strip().capitalize() or "Untitled Event"

    # Hardcoded datetime for demo
    dt = datetime.datetime(2025, 10, 12, 17, 0)  # 12 Oct 2025, 5 PM

    start_time = dt.isoformat()
    end_time = (dt + datetime.timedelta(hours=1)).isoformat()  # 1-hour duration

    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    event_link = created_event.get('htmlLink')
    return f"✅ Calendar event created: Meeting Scheduled"


