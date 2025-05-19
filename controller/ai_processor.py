#deep-seek model 
import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEESEEK_API_KEY = os.getenv("DEESEEK_API_KEY")
DEESEEK_API_URL = os.getenv("DEESEEK_API_URL")

headers = {
    "Authorization": f"Bearer {DEESEEK_API_KEY}",
    "Content-Type": "application/json"
}

def generate_response(chat_history, prompt, brand_name):
    system_message = (
        f"You are a professional business content writer. "
        f"Always write in third-person voice, using the brand's name ('{brand_name}'), 'the company', or 'the business' instead of 'we', 'our', or 'us'. "
        "Rewrite any input text by replacing first-person references with third-person formal references. "
        "Maintain a confident, clear, professional audit tone. "
        "Never use emojis. Never sound casual or promotional. "
        "Focus on providing factual, formal brand descriptions. "
        "Avoid using any asterisks (*) or unnecessary formatting marks."
    )

    chat_history.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_message}] + chat_history,
        "temperature": 0.7
    }

    response = requests.post(DEESEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    assistant_response = result["choices"][0]["message"]["content"]

    chat_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response, chat_history
