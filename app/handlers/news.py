# GENAI_ASSISTANT/app/handlers/news.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"

COUNTRY_MAP = {
    "india": "in",
    "united states": "us",
    "america": "us",
    "usa": "us",
    "japan": "jp",
    "germany": "de",
    "france": "fr",
    "china": "cn",
    "russia": "ru",
    "united kingdom": "gb",
    "uk": "gb",
    "canada": "ca",
    "australia": "au",
    "brazil": "br",
    "italy": "it",
    "south korea": "kr",
    "korea": "kr",
    "spain": "es",
    "mexico": "mx"
}

def extract_country(query: str) -> str:
    query_lower = query.lower()
    for name, code in COUNTRY_MAP.items():
        if name in query_lower:
            return code
    return "us"  # default country

def extract_category(query: str) -> str | None:
    categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    for cat in categories:
        if cat in query.lower():
            return cat
    return None

def handle_news(query: str) -> str:
    if not API_KEY:
        return "❌ News API key is missing. Please set NEWS_API_KEY in your .env file."

    print(f"[News Handler] → Fetching news for query: {query}")

    country_code = extract_country(query)
    category = extract_category(query)

    params = {
        "apiKey": API_KEY,
        "country": country_code,
        "pageSize": 5
    }

    if category:
        params["category"] = category

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return f"❌ Failed to fetch news. Status code: {response.status_code}"

    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        return "❌ No news articles found."

    headlines = [f"{i+1}. {article['title']}" for i, article in enumerate(articles)]

    country_name = next((name.title() for name, code in COUNTRY_MAP.items() if code == country_code), "the selected country")

    return f"📰 Top news headlines from {country_name}:\n" + "\n".join(headlines)


