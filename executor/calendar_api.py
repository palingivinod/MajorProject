import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_CREDENTIALS_PATH

# ---------------- CONFIG ----------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

CREDENTIALS_PATH = "D:/MajorProject/Assistant/config/googlecredentials.json" #GOOGLE_CREDENTIALS_PATH
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")

# ----------------------------------------

def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_event(slots: dict):
    try:
        service = get_calendar_service()

        title = slots.get("title", "Meeting")
        description = slots.get(
            "description", "Event created by AI Assistant"
        )

        try:
            start = datetime.fromisoformat(slots.get("start_time"))
        except:
            start = datetime.now() + timedelta(hours=1)

        try:
            end = datetime.fromisoformat(slots.get("end_time"))
        except:
            end = start + timedelta(hours=1)

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
        }

        service.events().insert(
            calendarId="primary", body=event
        ).execute()

        return f"📅 Event '{title}' added to Google Calendar."

    except Exception as e:
        return f"❌ Failed to create event: {e}"
