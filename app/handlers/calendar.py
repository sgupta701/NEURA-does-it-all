import datetime
import os
import pickle
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateparser.search import search_dates

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def extract_datetime_and_clean_summary(text: str):
    """
    Extracts the datetime mentioned in the text and returns cleaned summary and datetime object.
    """
    parsed = search_dates(text, settings={"PREFER_DATES_FROM": "future"})
    event_time = None

    if parsed:
        # Use the first parsed date
        matched_text, dt = parsed[0]
        event_time = dt

        # Remove the matched date text from the original input
        pattern = re.escape(matched_text)
        cleaned_summary = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    else:
        cleaned_summary = text

    # Clean up leading phrases
    cleaned_summary = cleaned_summary.lower().strip()
    prefixes = [
        "set a reminder to",
        "set a reminder for",
        "remind me to",
        "remind me about",
        "create an event to",
        "make a calendar event to"
    ]
    for prefix in prefixes:
        if cleaned_summary.startswith(prefix):
            cleaned_summary = cleaned_summary[len(prefix):].strip()
            break

    if cleaned_summary:
        cleaned_summary = cleaned_summary[0].upper() + cleaned_summary[1:]

    return cleaned_summary or "Untitled Event", event_time


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
    Uses actual time and date mentioned in the command if available.
    """
    summary, dt = extract_datetime_and_clean_summary(command)

    if dt is None:
        # fallback: schedule 1 hour from now
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    start_time = dt.isoformat()
    end_time = (dt + datetime.timedelta(hours=1)).isoformat()

    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Calendar event created: {created_event.get('htmlLink')}"
