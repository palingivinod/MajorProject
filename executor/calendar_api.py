import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# -------------------------------------------------
# Google Calendar config
# -------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "googlecredentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")


# -------------------------------------------------
# Auth + service creation
# -------------------------------------------------
def get_calendar_service():
    creds = None

    # ✅ Load existing token if present
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # ✅ If no valid creds, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # ✅ Save token for future runs
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# -------------------------------------------------
# Create calendar event (USED BY app.py)
# -------------------------------------------------
def create_event(slots: dict):
    try:
        service = get_calendar_service()

        # -------- Extract slots from LLM --------
        title = slots.get("title", "Meeting")
        description = slots.get(
            "description",
            "Event created using Offline AI Assistant"
        )

        start_time = slots.get("start_time")
        end_time = slots.get("end_time")

        # -------- SAFE datetime handling --------
        if isinstance(start_time, str):
            start = datetime.fromisoformat(start_time)
        else:
            start = datetime.now() + timedelta(hours=1)

        if isinstance(end_time, str):
            end = datetime.fromisoformat(end_time)
        else:
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
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 10}
                ],
            },
        }

        service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return f"📅 Event '{title}' created successfully."

    except Exception as e:
        return f"❌ Failed to create event: {e}"
