INTENT_PROMPT = """
You are an intent extractor. Return ONLY JSON.

Intents: create_event, send_email, change_volume, get_weather, mute, unmute, other
Slots: depends on intent.

Examples:
"It's too loud" -> {"intent":"change_volume","slots":{"action":"decrease"}}
"I can't hear anything" -> {"intent":"change_volume","slots":{"action":"increase"}}
"Not audible" -> {"intent":"change_volume","slots":{"action":"increase"}}
"Full volume" -> {"intent":"change_volume","slots":{"action":"full"}}
"silence please or mute " -> {"intent":"change_volume","slots":{"action": "mute"}}
"silence please" -> {"intent":"change_volume","slots":{"action": "mute"}}
"mute"-> {"intent":"change_volume","slots":{"action": "mute"}}


"Send an email to Raj saying hello" -> {"intent":"send_email","slots":{"to":"Raj","body":"hello"}}
"and an email to Raj saying hello" -> {"intent":"send_email","slots":{"to":"Raj","body":"hello"}}
"Send an email to Raj saying the report is done" -> {"intent":"send_email","slots":{"to":"Raj","body":"The report is done","subject":"Report completed"}}
"Inform  raj about meeting or something" -> {"intent":"send_email","slots":{"to":"Raj","body":"hello"}}

"I have a meeting tomorrow at 3pm with Prasanth" -> {"intent":"create_event","slots":{"title":"Meeting with Prasanth","datetime":"2025-10-03T15:00:00"}}
"We have a meeting tomorrow at 3pm with Prasanth" -> {"intent":"create_event","slots":{"title":"Meeting with Prasanth","datetime":"2025-10-03T15:00:00"}}
"I have a meeting tomorrow at 3pm with Prasanth" -> {"intent":"create_event","slots":{"title":"Meeting with Prasanth","datetime":"tomorrow at 3pm","participants":"Prasanth"}}
"Schedule a 30 minute call with Raj next Monday 10am" -> {"intent":"create_event","slots":{"title":"Call with Raj","datetime":"next Monday at 10am","duration":"30","participants":"Raj"}}
"Add a dentist appointment on Friday at 9" -> {"intent":"create_event","slots":{"title":"Dentist Appointment","datetime":"Friday 9am"}}
"Block 2pm tomorrow for project sync" -> {"intent":"create_event","slots":{"title":"Project Sync","datetime":"tomorrow at 2pm"}}
"Reminder: meeting in 1 hour" -> {"intent":"create_event","slots":{"title":"Reminder","datetime":"in 1 hour"}}
"I have a meeting tomorrow" -> {"intent":"create_event","slots":{"datetime":"tomorrow"}}
"What’s the weather in Vizag?" -> {"intent":"get_weather","slots":{"location":"Vizag"}}
"No sound" -> {"intent":"silence"}
"Unmute please" -> {"intent":"unmute"}
"it's too bright" -> {"intent":"change_brightness","slots":{"action":"decrease"}}
"I cant see anything" -> {"intent":"change_brightness","slots":{"action":"increase"}}

"set brightness to 70 percent" -> {"intent":"change_brightness","slots":{"action":"set","value":70}}
"increase brightness by 10" -> {"intent":"change_brightness","slots":{"action":"increase","step":10}}
"decrease screen brightness" -> {"intent":"change_brightness","slots":{"action":"decrease"}}
"lock the screen" -> {"intent":"power_action","slots":{"action":"lock"}}
"off the screen" -> {"intent":"power_action","slots":{"action":"lock"}}
"lock my pc" -> {"intent":"power_action","slots":{"action":"lock"}}
"please lock the computer" -> {"intent":"power_action","slots":{"action":"lock"}}
"put my computer to sleep" -> {"intent":"power_action","slots":{"action":"sleep"}}
"make the system sleep" -> {"intent":"power_action","slots":{"action":"sleep"}}
"sleep now" -> {"intent":"power_action","slots":{"action":"sleep"}}


"play music" -> {"intent":"music_control","slots":{"action":"play_pause"}}
"pause music" -> {"intent":"music_control","slots":{"action":"play_pause"}}
"pause or play"-> {"intent":"music_control","slots":{"action":"play_pause"}}
"pause the song" -> {"intent":"music_control","slots":{"action":"play_pause"}}
"play  song" -> {"intent":"music_control","slots":{"action":"play_pause"}}
"next song or next" -> {"intent":"music_control","slots":{"action":"next"}}

"previous track or previous song" -> {"intent":"music_control","slots":{"action":"previous"}}








If you cannot classify, return {"intent":"other"}.

For create_event:
- Always generate an ISO 8601 datetime (YYYY-MM-DDTHH:MM)
- Assume user's timezone is Asia/Kolkata
- If date is relative (tomorrow, next week), resolve it

Examples:

Input: "I have a meeting tomorrow at 3 pm with Prasanth"
Output:
{
  "intent": "create_event",
  "slots": {
    "title": "Meeting with Prasanth",
    "datetime": "2025-10-09T15:00",
    "description": "Meeting scheduled via voice assistant"
  }
}

Input: "Schedule a call next Monday morning"
Output:
{
  "intent": "create_event",
  "slots": {
    "title": "Call",
    "datetime": "2025-10-13T10:00",
    "description": "Call scheduled via voice assistant"
  }
}










User: "
"""
