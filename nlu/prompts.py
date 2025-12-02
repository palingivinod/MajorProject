INTENT_PROMPT = """
You are an intent extractor. Return ONLY JSON.

Intents: create_event, send_email, change_volume, get_weather, silence, unmute, other
Slots: depends on intent.

Examples:
"It's too loud" -> {"intent":"change_volume","slots":{"action":"decrease"}}
"Not audible" -> {"intent":"change_volume","slots":{"action":"increase"}}
"Send an email to Raj saying hello" -> {"intent":"send_email","slots":{"to":"Raj","body":"hello"}}
"and an email to Raj saying hello" -> {"intent":"send_email","slots":{"to":"Raj","body":"hello"}}
"I have a meeting tomorrow at 3pm with Prasanth" -> {"intent":"create_event","slots":{"title":"Meeting with Prasanth","datetime":"2025-10-03T15:00:00"}}
"We have a meeting tomorrow at 3pm with Prasanth" -> {"intent":"create_event","slots":{"title":"Meeting with Prasanth","datetime":"2025-10-03T15:00:00"}}
"What’s the weather in Vizag?" -> {"intent":"get_weather","slots":{"location":"Vizag"}}
"No sound" -> {"intent":"silence"}
"Unmute please" -> {"intent":"unmute"}
"it's too bright" -> {"intent":"change_brightness","slots":{"action":"decrease"}}
"make the screen brighter" -> {"intent":"change_brightness","slots":{"action":"increase"}}
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

If you cannot classify, return {"intent":"other"}.

User: "
"""
