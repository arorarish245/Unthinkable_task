# backend/app/llm_client.py
import os
from typing import Optional
from dotenv import load_dotenv
import httpx

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # put your key in .env

def generate_reply_openai(system: str, conversation: list, user_message: str) -> str:
    """
    Simple wrapper using OpenAI chat completions. Use whichever LLM provider you like.
    conversation: list of {"role":"user"/"assistant"/"system","content": "..."}
    """
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        messages = conversation + [{"role": "user", "content": user_message}]
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # replace with a model you have access to
            messages=messages,
            max_tokens=256,
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Fallback deterministic reply
        return "Sorry — I'm having trouble contacting the AI service. Please try again later."

def generate_reply_placeholder(system: str, conversation: list, user_message: str) -> str:
    # VERY simple placeholder rule-based reply used when you don't want to call an API.
    # We'll echo and suggest a next step.
    return f"I received: \"{user_message[:200]}\". If this is about orders, say 'order' to get more help."

# Choose which client to call from main.py (openai if key present otherwise placeholder)
