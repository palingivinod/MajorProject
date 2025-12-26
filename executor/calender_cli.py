"""
Small test CLI to verify calendar functions without voice UI.
Usage:
  python executor/calendar_cli.py create "meeting tomorrow 3pm" "Discuss release with team"
  python executor/calendar_cli.py list
  python executor/calendar_cli.py delete <event_id>
"""

import sys
from executor import calendar_api as cal

def main(argv):
    if len(argv) < 2:
        print("Usage: create <when> <title>, list, delete <id>, update <id> <start>")
        return
    cmd = argv[1].lower()
    if cmd == "create":
        when = argv[2] if len(argv) > 2 else "tomorrow 9am"
        title = argv[3] if len(argv) > 3 else "Voice-created meeting"
        slots = {"datetime": when, "title": title}
        print(cal.create_event(slots, transcript=f"Auto-created: {title}"))
    elif cmd == "list":
        items = cal.list_upcoming(10)
        for it in items:
            print(it)
    elif cmd == "delete":
        if len(argv) < 3:
            print("Provide event id to delete")
        else:
            print(cal.delete_event(argv[2]))
    elif cmd == "update":
        if len(argv) < 4:
            print("Usage: update <event_id> <new when>")
        else:
            print(cal.update_event(argv[2], {"start": argv[3]}))
    else:
        print("Unknown command:", cmd)

if __name__ == "__main__":
    main(sys.argv)
