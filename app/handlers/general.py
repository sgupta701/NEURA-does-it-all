# GENAI_ASSISTANT/app/handlers/general.py

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random
import re

class GeneralBot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.chat_history_ids = None
        self.max_history_len = 1000 

        self.generic_fallbacks = [
            "I'm sorry, I didn't quite get that. Could you please rephrase?",
            "That's interesting! Can you tell me more?",
            "I'm here to chat anytime. What's on your mind?",
            "Hmm, let's talk about something else. What would you like?",
            "Can you explain that a bit more?",
            "I want to understand better. Can you try again?",
            "Let's change the topic. What do you enjoy doing?",
            "I'm still learning, but I'm here to listen!",
            "Tell me more, please!",
            "Let's keep the conversation going!",
            "Sorry, I didn't catch that. Could you say it differently?",
            "Interesting! How does that make you feel?",
            "I love chatting with you! What else is new?",
            "That's cool! Want to share more?",
            "Can you say that in another way?",
            "Let's explore that idea further."
        ]

        self.keyword_fallbacks = {
            'joke': [
                "Here's a joke for you. Why don't scientists trust atoms? Because they make up everything!",
                "Here's a joke for you. Why did the scarecrow win an award? Because he was outstanding in his field!",
                "Here's a joke for you. I told my computer I needed a break, and now it won't stop sending me Kit-Kat ads!",
                "Here's a joke for you. Why don't programmers like nature? Too many bugs.",
                "Here's a joke for you. Why did the math book look sad? Because it had too many problems."
            ],
            'hello': [
                "Hello! How can I help you today?",
                "Hi there! What's on your mind?",
                "Hey! Great to see you. How can I assist?",
                "Hi! Ready for a chat?"
            ],
            'hi': [
                "Hello! How can I help you today?",
                "Hi there! What's on your mind?",
                "Hey! Great to see you. How can I assist?",
                "Hi! Ready for a chat?"
            ],
            'hoi': [
                "Hoiii! How can I help you today?",
                "Hoii! What's on your mind?",
                "Hey! Great to see you. How can I assist?",
                "Hoii! Ready for a chat?"
            ],
            'holaa': [
                "Holaaa! How can I help you today?",
                "Holaaa! What's on your mind?",
                "Holaaa! Great to see you. How can I assist?",
                "Holaaa! Ready for a chat?"
            ],
            'how are you': [
                "I'm a bot, so I don't have feelings, but thanks for asking! How about you?",
                "Doing great! Ready to chat with you.",
                "I'm here and ready to help. How's your day going?"
            ],
            'thanks': [
                "You're welcome!",
                "Anytime!",
                "Glad I could help!",
                "No problem!"
            ],
            'help': [
                "Sure! I would be happy to help",
            ],
            'few things': [
                "Sure! I would be happy to help",
            ],
            'bye': [
                "Goodbye! Have a great day!",
                "See you later!",
                "Take care!",
                "Bye! Come back soon."
            ]
        }

    def is_repetitive_or_empty(self, input_text, output_text):
        if not output_text.strip():
            return True
        input_clean = re.sub(r'\W+', '', input_text.lower())
        output_clean = re.sub(r'\W+', '', output_text.lower())
        if output_clean == input_clean:
            return True
        if len(output_text.split()) < 3:
            return True
        return False

    def check_keyword_fallback(self, input_text):
        lowered = input_text.lower()
        for keyword, responses in self.keyword_fallbacks.items():
            if keyword in lowered:
                return random.choice(responses)
        return None
    
    def is_safe_response(self, response: str) -> bool:
        bad_phrases = [
            "is the worst", "i hate", "you are stupid", 
            "kill yourself", "shut up", "you're dumb"
        ]
        lowered = response.lower()
        return not any(phrase in lowered for phrase in bad_phrases)


    def get_response(self, input_text, max_attempts=5):
        keyword_response = self.check_keyword_fallback(input_text)
        if keyword_response:
            return keyword_response

        new_input_ids = self.tokenizer.encode(input_text + self.tokenizer.eos_token, return_tensors='pt').to(self.device)

        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
            if bot_input_ids.size(1) > self.max_history_len:
                bot_input_ids = bot_input_ids[:, -self.max_history_len:]
        else:
            bot_input_ids = new_input_ids

        attention_mask = torch.ones(bot_input_ids.shape, dtype=torch.long, device=self.device)

        for attempt in range(max_attempts):
            try:
                output_ids = self.model.generate(
                    bot_input_ids,
                    max_length=bot_input_ids.shape[-1] + 50,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    top_p=0.9,
                    temperature=0.8,
                    attention_mask=attention_mask,
                    num_return_sequences=1
                )
                response = self.tokenizer.decode(output_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True).strip()

                if self.is_safe_response(response) and not self.is_repetitive_or_empty(input_text, response):
                    self.chat_history_ids = output_ids 
                    return response
            except Exception as e:
                continue

        # if nothing good generated, random fallback is picked
        fallback = random.choice(self.generic_fallbacks)
        return fallback

general_bot = GeneralBot()

def handle_general(command: str) -> str:
    return general_bot.get_response(command)


