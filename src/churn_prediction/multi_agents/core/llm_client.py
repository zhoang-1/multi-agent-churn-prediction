# core/llm_client.py
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    prompt = f"{system_prompt}\n\n------------------------\n{user_prompt}"
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text