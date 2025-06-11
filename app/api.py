# GENAI_ASSISTANT/app/api.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.query_splitter import QuerySplitter
from app.intent_classifier import IntentClassifier
from app.langchain_agent import route_command
from app.handlers.email_handler import handle_email

# FastAPI 
app = FastAPI()

# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models 
class ChatRequest(BaseModel):
    text: str

# NLP components 
splitter = QuerySplitter()
classifier = IntentClassifier()

# Chat endpoint 
@app.post("/chat")
async def chat(req: ChatRequest):
    segments = splitter.split_query(req.text)
    answers = []

    for q in segments:
        intent = classifier.classify_intent(q)
        try:
            if intent == "email":
                answers.append(handle_email(q))
            else:
                answers.append(route_command(q, intent))
        except Exception as e:
            answers.append(f"❌ {e}")

    return {"segments": segments, "answers": answers}
