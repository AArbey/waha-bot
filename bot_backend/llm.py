
import os
import requests

from .config import LLM_URL, LLM_MODEL

def ask_ai(message, recent_messages=None):
    # Read instructions from "instructions.txt" file
    with open("instructions.txt", "r") as f:
        instructions = f.read()

    messages = [
        {"role": "system", "content": instructions},
        *(recent_messages or []),
        message,
    ]


    headers = {}
    if key := os.getenv("LLM_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"

    response = requests.post(
        f"{LLM_URL.rstrip('/')}/chat/completions",
        headers=headers,
        json={
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "stream": False,
            "cache_prompt": True,
        },
        timeout=(10, 300),
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]