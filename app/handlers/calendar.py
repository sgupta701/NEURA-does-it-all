import datetime
import os
import pickle
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser as dtparser  # more reliable datetime parsing

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def extract_summary_date_time(text: str):
    # Normalize
    text = text.strip().lower()

    # Remove prefixes
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
            text = text[len(prefix):].strip()
            break

    # Match using 'on ... at ...'
    match = re.search(r"(.+?)\s+on\s+(.+?)\s+at\s+(.+)", text)
    if not match:
        return text, None  # fallback

    summary = match.group(1).strip().capitalize()
    date_part = match.group(2).strip()
    time_part = match.group(3).strip()

    # Parse datetime safely
    try:
        full_str = f"{date_part} {time_part}"
        dt = dtparser.parse(full_str)
    except:
        dt = None

    return summary or "Untitled Event", dt


def get_calendar_service():
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
    summary, dt = extract_summary_date_time(command)

    if dt is None:
        dt = datetime.datetime.now() + datetime.timedelta(hours=1)

    start_time = dt.isoformat()
    end_time = (dt + datetime.timedelta(hours=1)).isoformat()

    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    event_link = created_event.get('htmlLink')
    return f"✅ Calendar event created: {summary}\n{event_link}"

