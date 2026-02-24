import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def reply_to_me(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # Telegram has a 4096 character limit per message
    # If output is long, split it into chunks
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        req = requests.post(url, json={"chat_id": CHAT_ID, "text": chunk})
        print(req.status_code)
        print(req.json())