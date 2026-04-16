import webbrowser
import os
import subprocess
import urllib.parse

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "twitter": "https://twitter.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "mvgr": "https://www.mvgrce.com"
}


APP_PATHS = {
    "chrome": r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    "whatsapp": os.path.expandvars(r"%LocalAppData%/WhatsApp/WhatsApp.exe"),
    "vlc": r"C:/Program Files/VideoLAN/VLC/vlc.exe",
    "spotify": os.path.expandvars(r"%AppData%/Spotify/Spotify.exe")
}


def open_site(slots):
    name = slots.get("site", "").lower()
    print(f"Requested to open: {name}")
    if not name:
        return " Website name missing."

    # Check installed app
    if name in APP_PATHS and os.path.exists(APP_PATHS[name]):
        try:
            subprocess.Popen(APP_PATHS[name])
            return f"Opened {name} application."
        except:
            pass

    # 2️⃣ Fallback to website
    if name in WEBSITES:
        webbrowser.open(WEBSITES[name])
        return f"Opened {name} in browser."

    return "Website or application not supported."



def open_browser():
    webbrowser.open("https://www.google.com")
    return "Browser opened with Google."

def smart_search(slots):
    platform = slots.get("platform", "").lower()
    query = slots.get("query", "")

    if not query:
        return "Search query missing."

    encoded_query = urllib.parse.quote_plus(query)

    # GOOGLE SEARCH
    if platform == "google" or platform == "":
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"Searching for {query} on Google."
    elif platform == "wikipedia":
        url = f"https://en.wikipedia.org/w/index.php?search={encoded_query}"
        webbrowser.open(url)
        return f"Searching Wikipedia for {query}."
    # YOUTUBE SEARCH
    elif platform == "youtube":
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}."

    # AMAZON SEARCH
    elif platform == "amazon":
        url = f"https://www.amazon.in/s?k={encoded_query}"
        webbrowser.open(url)
        return f"Searching Amazon for {query}."

    # FLIPKART SEARCH
    elif platform == "flipkart":
        url = f"https://www.flipkart.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"🛍 Searching Flipkart for {query}."

    else:
        return "Search platform not supported."
