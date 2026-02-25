from database.telegram_db import get_telegram_history, save_telegram_message
from llm.gemini_llm import call_gemini_raw
from logger import get_logger


log = get_logger(__name__)


def get_system_prompt() -> str:
    try:
        with open("system_prompt.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a concise Termux Linux assistant."


async def handle_telegram_chat(user_message: str) -> str:
    """
    Get response to user message sent on telegram
    """
    # 1. Fetch history
    history = await get_telegram_history(limit=10)
    
    # 2. Append new message
    history.append({"role": "user", "parts": [{"text": user_message}]})
    
    # 3. Build payload
    payload = {
        "systemInstruction": {"parts": [{"text": get_system_prompt()}]},
        "contents": history
    }
    
    # 4. Call Gateway
    try:
        response_text = await call_gemini_raw(payload, caller="telegram")
    except Exception as e:
        log.error(f"Pipeline failed: {e}")
        return "⚠️ Brain connection failed."

    # 5. Persist to SQLite
    await save_telegram_message("user", user_message)
    await save_telegram_message("model", response_text)
    
    return response_text