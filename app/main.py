# GENAI_ASSISTANT/app/main.py

from dotenv import load_dotenv
load_dotenv()

from app.query_splitter import QuerySplitter
from app.intent_classifier import IntentClassifier
from app.langchain_agent import route_command  
from app.handlers.email_handler import handle_email  

def main():
    splitter = QuerySplitter()
    classifier = IntentClassifier()

    #input from user
    input_text = input("Please enter your query (you can enter multiple commands): ")

    #split input into multiple queries
    segments = splitter.split_query(input_text)

    print("\n[Segmented Queries]")
    for i, s in enumerate(segments, 1):
        print(f"{i}. {s}")

    print("\n[Responses]")

    #intent for each queryy
    for query in segments:
        intent = classifier.classify_intent(query)

        #completing user request
        if "email" in intent:
            response = handle_email(query)  
        else:
            response = route_command(query, intent)

        print(f"Input: {query}\nIntent: {intent}\nResponse: {response}")


if __name__ == "__main__":
    main()

