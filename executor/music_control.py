import os
import subprocess
import tempfile
from pynput.keyboard import Key, Controller
import  glob

keyboard = Controller()

def open_music():
    try:
        music_dir = "C:/Users/vinod/Music/Playlists"

        audio_files = []
        for ext in ("*.mp3", "*.wav", "*.m4a", "*.flac"):
            audio_files.extend(glob.glob(os.path.join(music_dir, ext)))

        if not audio_files:
            return " No music files found in your Music folder."

        # Create temporary playlist
        playlist_path = os.path.join(
            tempfile.gettempdir(), "assistant_music_playlist.m3u"
        )

        with open(playlist_path, "w", encoding="utf-8") as f:
            for song in audio_files:
                f.write(song + "\n")

        # Open playlist → default music player
        os.startfile(playlist_path)

        return "🎵 Music playlist opened. Play, pause, next and previous are now enabled."

    except Exception as e:
        return f"Failed to open music: {e}"

    
def play_pause():
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)
    return " Play / Pause toggled."

def next_track():
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)
    return "Playing next track."

def previous_track():
    keyboard.press(Key.media_previous)
    keyboard.release(Key.media_previous)
    keyboard.press(Key.media_previous)
    return "Playing previous track."

import subprocess

def close_music():
    """
    Close common Windows media players safely
    """
    players = [
        "wmplayer.exe",     # Windows Media Player
        "vlc.exe",          # VLC
        "Music.UI.exe",     # Groove Music
        "Spotify.exe"
    ]

    closed = False

    for player in players:
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", player],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            closed = True
        except:
            pass

    if closed:
        return "Music player closed."
    else:
        return "No active music player found."
