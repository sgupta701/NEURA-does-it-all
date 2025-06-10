#GENAI_ASSISTANT/app/handlers/weather.py
 
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def extract_city(query: str) -> str:
    # basic approach to extract a location (planning spaCy for smarter extraction later)
    words = query.lower().split()
    for i, word in enumerate(words):
        if word in ["in", "at", "for"]:
            if i + 1 < len(words):
                return words[i + 1]
    return "Delhi"  # default 

def handle_weather(query: str) -> str:
    city = extract_city(query)

    print(f"[Weather Handler] → Checking weather for: {city}")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return f"❌ Couldn't fetch weather for '{city}'."

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]

        return f"🌤️ Weather in {city.capitalize()}: {weather}, {temp}°C (feels like {feels_like}°C)"
    except Exception as e:
        return f"❌ Error fetching weather: {str(e)}"
