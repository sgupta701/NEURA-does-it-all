from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

class QuerySplitter:
    
    def __init__(self, model_name="./app/finetuned_query_splitter"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.eval()

    def format_prompt(self, input_query):
        prompt = (
            "Input: Schedule a meeting with Saumya tomorrow and play some music.\n"
            "Segments:\n"
            "1. Schedule a meeting with Saumya tomorrow.\n"
            "2. Play some music.\n\n"

            "Input: What's the weather today and play shape of you and schedule an event at 4 pm on September 9, 2025.\n"
            "Segments:\n"
            "1. What's the weather today.\n"
            "2. Play shape of you.\n"
            "3. Schedule an event at 4 pm on September 9, 2025.\n\n"

            "Input: Choose a number between 1 and 100, mail Utkarsh that I'm okay and ask when he's back from America, then play Rasputin.\n"
            "Segments:\n"
            "1. Choose a number between 1 and 100.\n"
            "2. Mail Utkarsh that I'm okay and ask when he's back from America.\n"
            "3. Play Rasputin.\n\n"

            "Input: Send a message to Mom saying I'm safe and will call tonight, and also play without me.\n"
            "Segments:\n"
            "1. Send a message to Mom saying I'm safe and will call tonight.\n"
            "2. Play without me.\n\n"

            "Input: From where do I buy some paint and brushes? Also, write a mail to my friend Utkarsh at utkarshg@gmail.com that I am fine and my flight has landed, then play Kings & Queens by Ava Max. Ok, Bye!!\n"
            "Segments:\n"
            "1. From where do I buy some paint and brushes?\n"
            "2. Write a mail to my friend Utkarsh at utkarshg@gmail.com that I am fine and my flight has landed.\n"
            "3. Play Kings & Queens by Ava Max.\n"
            "4. Ok, Bye!!\n\n"

            f"Input: {input_query.strip()}\n"
            "Segments:\n"
        )
        return prompt

    def smart_fallback_split(self, query):
        protected = {}

        #protect email addresses
        def protect_emails(text):
            matches = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            for i, match in enumerate(matches):
                key = f"__EMAIL{i}__"
                protected[key] = match
                text = text.replace(match, key)
            return text

        # protect compound phrases 
        def protect_phrases(text):
            compound_phrases = [
                "kabaddi and kho-kho",
                "you and me",
                "kings and queens",
                "mom and dad"
            ]
            for i, phrase in enumerate(compound_phrases):
                matches = re.finditer(re.escape(phrase), text, flags=re.IGNORECASE)
                for j, match in enumerate(matches):
                    start = max(0, match.start() - 25)
                    context = text[start:match.end()].lower()
                    if any(word in context for word in ['play', 'music', 'song']):
                        continue  
                    key = f"__PHRASE{i}_{j}__"
                    protected[key] = match.group()
                    text = text.replace(match.group(), key)
            return text

        query = protect_emails(query)
        query = protect_phrases(query)

        #split on punctuation and conjunctions
        parts = re.split(r'[?!.]+[\s\n]*', query)
        temp_segments = []
        for part in parts:
            sub_segments = re.split(r'\b(?:then|also|and then|, then|, also|and)\b', part, flags=re.IGNORECASE)
            temp_segments.extend(sub_segments)

        segments = [s.strip(" ,.\n") for s in temp_segments if s.strip(" ,.\n")]

        #restoring protected content
        restored_segments = []
        for seg in segments:
            for key, val in protected.items():
                seg = seg.replace(key, val)
            restored_segments.append(seg)

        return restored_segments

    def parse_segments(self, decoded_output):
        """
        Extract segments robustly from model output text.
        """
        try:
            segments_text = decoded_output.split("Segments:")[-1].strip()
            lines = [line.strip() for line in segments_text.split('\n') if line.strip()]
            segments = []
            for line in lines:
                segment = re.sub(r'^\d+\.\s*', '', line)
                if segment:
                    segments.append(segment)
            return segments
        except Exception as e:
            print("[Error parsing segments]:", e)
            return []

    def split_query(self, input_query, max_tokens=150):
        prompt = self.format_prompt(input_query)
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=False,
                num_beams=4,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        decoded_output = self.tokenizer.decode(output[0], skip_special_tokens=True)

        lines = decoded_output.split("Segments:")[-1].strip().split("\n")
        segments = [
            line.strip("1234567890.- ").strip()
            for line in lines
            if line.strip()
        ]

        #if model returns kess than 1 segment, fallback to naive splitting logic
        if len(segments) <= 1:
            segments = self.smart_fallback_split(input_query)

        return segments if segments else [input_query]
