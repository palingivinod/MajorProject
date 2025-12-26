from pynput.keyboard import Key, Controller

keyboard = Controller()

def play_pause():
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)
    return " Play / Pause toggled."

def next_track():
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)
    return "Next track."

def previous_track():
    keyboard.press(Key.media_previous)
    keyboard.release(Key.media_previous)
    return "Previous track."
