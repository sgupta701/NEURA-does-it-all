# GENAI_ASSISTANT/app/intent_classifier.py

from transformers import pipeline

class IntentClassifier:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

    def classify_intent(self, query: str) -> str:
        query_lower = query.lower()

        if "email" in query_lower or "mail" in query_lower or "message" in query_lower or "update" in query_lower:
            return "email"
        elif "meeting" in query_lower or "calendar" in query_lower or "schedule" in query_lower or "reminder" in query_lower or "alarm" in query_lower:
            return "calendar"
        elif "music" in query_lower or "song" in query_lower or "play" in query_lower or "hear" in query_lower:
            return "music"
        elif "weather" in query_lower or "rain" in query_lower or "forecast" in query_lower or "temperature" in query_lower or "humidity" in query_lower or "heat" in query_lower or "snow" in query_lower or "climate" in query_lower:
            return "weather"
        elif "news" in query_lower or "headlines" in query_lower or "stories" in query_lower:
            return "news"

        else:
            return "general"

