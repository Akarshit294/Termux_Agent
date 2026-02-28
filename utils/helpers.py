import aiohttp
from .config import config
from .logger import get_logger


log = get_logger(__name__)

async def reply_to_me(text: str):
    """
    Function to send message on Telegram using aiohttp for consistency.
    """
    url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"

    # Telegram has a 4096 character limit per message
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]

    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            async with session.post(url, json={"chat_id": config.chat_id, "text": chunk}) as resp:
                try:
                    data = await resp.json()
                except Exception:
                    data = {"error": "invalid JSON response"}

                log.info(f"Telegram reply: {chunk}, status_code: {resp.status}, response: {data}")
