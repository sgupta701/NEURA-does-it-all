# GENAI_ASSISTANT/app/handlers/local_llm_generator.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests

class LocalLLMGenerator:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"

    def generate_text(self, prompt):
        try:
            response = requests.post(self.base_url, json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.RequestException as e:
            return f"[Error contacting local LLM: {e}]"


# test
if __name__ == "__main__":
    gen = LocalLLMGenerator()
    prompt = "Write a email to inform my boss that I cannot attend the meeting tomorrow due to some urgent work."
    print(gen.generate_text(prompt))
