# GENAI_ASSISTANT/app/langchain_agent.py

from app.handlers import calendar
from app.handlers import music
from app.handlers import email_handler
from app.handlers import weather
from app.handlers import news
from app.handlers import general

INTENT_ROUTER = {
    "calendar": calendar.handle_calendar,
    "music": music.handle_music,
    "email": email_handler.handle_email,
    "weather": weather.handle_weather,
    "news": news.handle_news,
    "general": general.handle_general,
}

def route_command(command: str, intent: str):
    handler = INTENT_ROUTER.get(intent, general.handle_general)
    return handler(command)
