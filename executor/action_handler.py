from executor.volume_control import change_volume

def handle_action(intent_data):
    intent = intent_data.get("intent")
    slots = intent_data.get("slots", {})

    if intent == "silence":
        # mute the system
        return "🔇 System muted (silence intent)"

    elif intent == "unmute":
        return "🔊 System unmuted"

    elif intent == "change_volume":
        result = change_volume(slots)
        return result

    elif intent == "share_project":
        recipient = slots.get("recipient", "someone")
        # Here you can integrate email sending / file sharing logic
        return f"📤 Project details sent to {recipient} (simulated)"

    else:
        return f"⚠️ Intent not recognized, fallback: {intent}"

