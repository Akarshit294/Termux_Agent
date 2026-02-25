import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from helpers import BOT_TOKEN, CHAT_ID, reply_to_me
from llm.llm_gateway import llm_worker
from pipeline.telegram_pipeline import handle_telegram_chat
from database.telegram_db import init_db, clear_telegram_history

from dotenv import load_dotenv
from logger import get_logger


log = get_logger(__name__, process_name = "main")
load_dotenv()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_authorized(message: types.Message) -> bool:
    """
    Only respond to my messages
    """
    return str(message.chat.id) == str(CHAT_ID)


@dp.message(Command("clear"))
async def handle_clear_command(message: types.Message):
    """The Memory Reset Switch"""
    if not is_authorized(message): return
    
    await clear_telegram_history()
    
    try:
        await message.delete()
    except Exception:
        pass
        
    separator = "━" * 40
    blank_slate = (
        "\n" * 15 +  # push content off screen
        f"{separator}\n"
        f"🧹   MEMORY CLEARED   🧹\n"
        f"{separator}\n"
        "\n" * 5 +
        "✨ Fresh start. Clean slate. ✨"
    )
    await reply_to_me(blank_slate)


@dp.message()
async def handle_message(message: types.Message):
    """
    Telegram's decorator for handling incoming messages
    """
    if not is_authorized(message):
        return  

    text = message.text.strip()
    log.info("User Message: %s", text)

    if text.startswith("!run "):
        command = text[len("!run "):]
        await reply_to_me(f"⚡ Run command: `{command}`")
        return

    response = await handle_telegram_chat(text)
    await reply_to_me(response)


async def main():
    """
    1. Sends Online message.
    2. Runs Polling task asynchronously.
    """
    log.info("MAIN STARTED!")
    await init_db()
    log.info("Database verified.")

    await reply_to_me("Termux agent is online.")

    llm_task = asyncio.create_task(llm_worker())
    polling_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(llm_task, polling_task)


if __name__ == "__main__":
    asyncio.run(main())