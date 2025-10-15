import requests

# Replace this with your actual WeatherAPI key
API_KEY = "1a2f20bcf51e4ad39c884648250710"

BASE_URL = "http://api.weatherapi.com/v1"

def get_weather(slots):
    """
    Fetch weather information from WeatherAPI based on slots (location, datetime).
    """
    location = slots.get("location", "Vizag")
    date = slots.get("datetime", "today")

    try:
        # Choose endpoint based on date
        if date.lower() in ["today", "now"]:
            url = f"{BASE_URL}/current.json?key={API_KEY}&q={location}"
            res = requests.get(url)
            data = res.json()
            print(data)

            if "error" in data:
                return f"❌ Couldn't fetch weather for {location}: {data['error']['message']}"

            temp = data["current"]["temp_c"]
            cond = data["current"]["condition"]["text"]
            feels = data["current"]["feelslike_c"]
            return f"🌤️ Weather in {location}: {cond}, {temp}°C (feels like {feels}°C)."

        else:
            # Forecast for future day (e.g., tomorrow)
            url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={location}&days=2"
            res = requests.get(url)
            data = res.json()

            if "error" in data:
                return f"❌ Couldn't fetch forecast for {location}: {data['error']['message']}"

            forecast = data["forecast"]["forecastday"][1]["day"]
            condition = forecast["condition"]["text"]
            avg_temp = forecast["avgtemp_c"]
            rain = forecast["daily_chance_of_rain"]
            return f"🌦️ Tomorrow in {location}: {condition}, Avg {avg_temp}°C, Chance of rain: {rain}%."

    except Exception as e:
        return f"⚠️ Weather fetch failed: {e}"
        print("Exception")



