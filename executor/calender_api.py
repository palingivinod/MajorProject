# executor/calendar_api.py
"""
Google Calendar helper for local voice assistant.

Provides:
  - get_calendar_service()       # returns googleapiclient service
  - create_event(slots, transcript="")  # create event using slots
  - list_upcoming(n=5)          # returns list of upcoming events
  - delete_event(event_id)      # delete by id
  - update_event(event_id, slots)  # update simple fields

Notes:
 - Expects Google OAuth client credentials json at config/credentials.json
 - Token is saved to config/token.pickle after first auth
 - Uses dateparser to parse natural language datetimes
 - Optional: uses local Ollama (cfg.OLLAMA_MODEL) to generate descriptions
"""

import os
import pickle
import subprocess
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict

import dateparser
from dateutil import tz

# Dependencies from google
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Config paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")  # Google OAuth client secrets
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.pickle")

# Google Calendar scope
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Optional local LLM (ollama) config - read from config.settings if present
try:
    import config.settings as cfg
    OLLAMA_BIN = getattr(cfg, "OLLAMA_BIN", "ollama")
    OLLAMA_MODEL = getattr(cfg, "OLLAMA_MODEL", None)
    OLLAMA_TIMEOUT = getattr(cfg, "OLLAMA_TIMEOUT", 6)
except Exception:
    OLLAMA_BIN = "ollama"
    OLLAMA_MODEL = None
    OLLAMA_TIMEOUT = 6


# -------------------------
# Google Calendar Service
# -------------------------
def get_calendar_service():
    """Get Google Calendar service (v3). Performs OAuth flow on first run."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, "rb") as f:
                creds = pickle.load(f)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Missing Google credentials file at {CREDENTIALS_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # save token
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
    service = build("calendar", "v3", credentials=creds)
    return service


# -------------------------
# Date parsing utilities
# -------------------------
def _parse_datetime(natural_text: Optional[str], prefer_future=True) -> Optional[datetime]:
    if not natural_text:
        return None
    settings = {"PREFER_DATES_FROM": "future" if prefer_future else "current_period"}
    dt = dateparser.parse(natural_text, settings=settings)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.tzlocal())
    return dt


def _to_rfc3339(dt: datetime) -> str:
    return dt.astimezone(tz.tzutc()).isoformat()


# -------------------------
# LLM-based description (optional)
# -------------------------
def generate_description_with_llm(transcript: str) -> Optional[str]:
    """Use local ollama to produce a short event description. Returns None on failure."""
    if not OLLAMA_MODEL or not transcript:
        return None
    prompt = (
        "You are concise. Generate a 1-2 sentence calendar event description from this user sentence.\n\n"
        f"User: \"{transcript}\"\n\nDescription:"
    )
    try:
        proc = subprocess.run(
            [OLLAMA_BIN, "run", OLLAMA_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=OLLAMA_TIMEOUT,
        )
        out = proc.stdout.decode("utf-8", errors="ignore").strip()
        if not out:
            return None
        # first non-empty line
        for line in out.splitlines():
            if line.strip():
                return line.strip()[:400]
        return None
    except Exception:
        return None


# -------------------------
# Core event functions
# -------------------------
def create_event(slots: Dict, transcript: str = "") -> str:
    """
    Create an event from slots. Supported slots:
      - title, datetime, start, end, duration (minutes), participants (comma), location, description
    """
    title = slots.get("title") or slots.get("summary") or "Meeting"
    datetime_text = slots.get("datetime") or slots.get("when") or slots.get("start")
    duration_min = None
    if "duration" in slots:
        try:
            duration_min = int(slots.get("duration"))
        except Exception:
            duration_min = None

    participants = slots.get("participants") or slots.get("people") or slots.get("to") or ""
    location = slots.get("location", "")
    description = slots.get("description", "")

    # auto-generate description from transcript via LLM if not provided
    if not description and transcript:
        gen = generate_description_with_llm(transcript)
        if gen:
            description = gen
    if not description:
        description = f"Created via Voice Assistant: {transcript[:200]}"

    # parse start datetime
    dt = None
    if datetime_text:
        dt = _parse_datetime(datetime_text, prefer_future=True)
    if not dt and transcript:
        dt = _parse_datetime(transcript, prefer_future=True)
    # default to tomorrow 09:00
    if not dt:
        now = datetime.now(tz.tzlocal())
        dt = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

    start_dt = dt
    if duration_min:
        end_dt = start_dt + timedelta(minutes=duration_min)
    else:
        end_dt = start_dt + timedelta(hours=1)

    attendees = []
    if participants:
        # split on commas and "and"
        parts = []
        for part in participants.split(","):
            for p in part.split(" and "):
                p = p.strip()
                if p:
                    if "@" in p:
                        attendees.append({"email": p})
                    else:
                        attendees.append({"displayName": p})

    event = {
        "summary": title,
        "location": location,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": str(start_dt.tzinfo)},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": str(end_dt.tzinfo)},
        "attendees": attendees,
        "reminders": {"useDefault": True},
    }

    try:
        service = get_calendar_service()
        created = service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()
        ev_id = created.get("id")
        start_h = start_dt.astimezone(tz.tzlocal()).strftime("%b %d %Y %I:%M %p")
        return f"Event created: {title} at {start_h} (id: {ev_id})"
    except Exception as e:
        return f"Failed to create event: {e}"


def list_upcoming(n: int = 5) -> List[Dict]:
    """Return upcoming n events (basic dicts)."""
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(calendarId="primary", timeMin=now, maxResults=n, singleEvents=True, orderBy="startTime")
            .execute()
        )
        items = events_result.get("items", [])
        results = []
        for it in items:
            start = it.get("start", {}).get("dateTime", it.get("start", {}).get("date"))
            results.append({"id": it.get("id"), "summary": it.get("summary"), "start": start})
        return results
    except Exception as e:
        return [{"error": str(e)}]


def delete_event(event_id: str) -> str:
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return f" Event {event_id} deleted."
    except Exception as e:
        return f"Failed to delete event: {e}"


def update_event(event_id: str, slots: Dict) -> str:
    """
    Minimal update: updates summary, start, end, description.
    slots keys: title/summary, start (natural), duration (min), description
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if "title" in slots or "summary" in slots:
            event["summary"] = slots.get("title", slots.get("summary", event.get("summary")))

        if "description" in slots:
            event["description"] = slots.get("description")

        # update start/end if start provided
        if "start" in slots or "datetime" in slots:
            dt = _parse_datetime(slots.get("start") or slots.get("datetime"))
            if dt:
                event["start"] = {"dateTime": dt.isoformat(), "timeZone": str(dt.tzinfo)}
                duration_min = int(slots.get("duration") or 60)
                event["end"] = {"dateTime": (dt + timedelta(minutes=duration_min)).isoformat(), "timeZone": str(dt.tzinfo)}

        updated = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        return f"Event updated: {updated.get('id')}"
    except Exception as e:
        return f"Failed to update event: {e}"
