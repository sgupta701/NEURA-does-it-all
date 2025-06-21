# GENAI_ASSISTANT/app/handlers/email_handler.py

import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
import re

from app.handlers.local_llm_generator import LocalLLMGenerator
llm_generator = LocalLLMGenerator()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "app/handlers/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def infer_subject(query: str) -> str:
    subject_cases = [
        # Unavailability
        (["not attend", "can't attend", "unable to attend", "absent", "won't be able to attend"], "Unable to Attend Meeting"),
        (["reschedule", "postpone", "delay meeting", "delay call"], "Meeting Rescheduling"),
        # Follow-ups 
        (["reminder", "gentle reminder"], "Gentle Reminder"),
        # meetings 
        (["schedule meeting", "set up meeting", "arrange a meeting", "book a meeting"], "Meeting Request"),
        (["confirm meeting", "confirm schedule"], "Meeting Confirmation"),
        # apology 
        (["apologize", "apology", "sorry for"], "Apology Regarding Recent Issue"),
        # gratitude
        (["thank you", "thanks", "grateful", "appreciate"], "Thank You"),
        # feedback
        (["feedback", "review", "comments", "opinion"], "Request for Feedback"),
        # Submissions & reports
        (["submit", "submission", "assignment", "report", "document"], "Submission Confirmation"),
        # application or request
        (["apply for", "interested in", "job role", "position"], "Application for Opportunity"),
        # follow up
        (["follow up", "follow up for job", "application status"], "Follow up on Job Application"),
        # good news
        (["promotion", "new job", "got hired", "accepted offer"], "Exciting Career Update"),
        (["engaged", "wedding", "getting married"], "Happy Personal News"),
        (["pregnant", "baby", "expecting"], "Exciting Family News"),
        # sensitive updates
        (["passed away", "sad news", "loss", "grieving", "funeral"], "Condolence & Support"),
        (["health issue", "sick", "diagnosed", "hospital", "not well", "feeling low", "fever"], "Personal Health Update"),
        # questions
        (["have a question", "need clarification", "could you help"], "Quick Clarification Request"),
        # work Issues
        (["bug", "issue", "error", "problem", "crash", "not working"], "Issue Report"),
        (["deployment", "release", "launch"], "Product Deployment Update"),
        # invitations
        (["party", "invitation", "celebrate"], "You're Invited!"),
        # catch-up
        (["catch up", "long time", "how are you"], "Let's Catch Up"),
        # wishing birthday
        (["happy birthday"], "Happy Birthday!!"),
        # wishing marriage anniversary
        (["happy marriage anniversary", "happy wedding anniversary"], "Happy Marriage Anniversary!!"),
        # Default
        ([], "Important Update"),
    ]

    lowered = query.lower()
    for keywords, subject in subject_cases:
        if any(k in lowered for k in keywords):
            return subject

    return "Important Update"


def extract_sender_name(query: str) -> str:
    match = re.search(r"\bi\s*\((\w+)\)", query, re.IGNORECASE)
    return match.group(1) if match else "I"


def handle_email(query: str) -> str:
    print(f"[Email Handler] → Generating email from query: {query}")

    sender = extract_sender_name(query)
    subject_line = infer_subject(query)

    # prompt LLM
    prompt = (
        f"User request: {query}\n\n"
        f"The sender is: {sender}\n\n"
        "Write a polite and clear concise email body based on the above request with no irrelevant content or hallucinations.\n"
        "DO NOT repeat anything twice.\n"
        "DO NOT include any subject line, salutation, closing, or notes.\n"
        "ONLY return the plain email body content.\n"
    )

    raw_output = llm_generator.generate_text(prompt).strip()

    def clean_output(text):
        for cutoff in ["The sender is:", "User request:", "Write a polite"]:
            if cutoff in text:
                text = text.split(cutoff)[-1].strip()
        match = re.search(r"([A-Z][^\n]+(?:\n|$).*)", text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    generated_email = clean_output(raw_output)

    # Remove trailing common closings
    for stop_phrase in ["Note:", "Thanks", "Thank you", "Sincerely", "Regards"]:
        if stop_phrase in generated_email:
            generated_email = generated_email.split(stop_phrase)[0].strip()

    # extract recipient
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", query)
    to = email_match.group(0) if email_match else "recipient@example.com"

    # typo check
    typo_domains = {
        "gamil.com": "gmail.com",
        "gmial.com": "gmail.com",
        "gnail.com": "gmail.com",
        "hotnail.com": "hotmail.com",
        "yaho.com": "yahoo.com",
        "outlok.com": "outlook.com",
        "rediffmai.com": "rediffmail.com",
        "icloud.co": "icloud.com"
    }

    try:
        user_part, domain_part = to.split("@")
        if domain_part in typo_domains:
            suggested = typo_domains[domain_part]
            return f"⚠️ Email not sent.\nPossible typo in email address: `{domain_part}`\nDid you mean: `{user_part}@{suggested}`?"
    except ValueError:
        return "❌ Invalid email address format."

    # compose and send email
    message = EmailMessage()
    message.set_content(generated_email)
    message["To"] = to
    message["From"] = "me"
    message["Subject"] = subject_line

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service = get_gmail_service()
    sent_message = service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()

    print(f"To: {to}")
    print(f"Subject: {subject_line}")
    print(f"Body:\n{generated_email}")

    return f"📤 Email sent!\nTo: {to}\nSubject: {subject_line}\nMessage ID: {sent_message['id']}"
