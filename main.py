import asyncio
from aiogram import Bot, Dispatcher, types, Router

from utils.config import config
from utils.helpers import reply_to_me
from llm.llm_gateway import llm_worker
from pipeline.telegram_pipeline import handle_telegram_chat
from database.telegram_db import init_db
from handlers.telegram_commands import admin_router
from services.task_manager import TaskManager
from middlewares import AuthMiddleware

from utils.logger import get_logger


log = get_logger(__name__, process_name = "main")

bot = Bot(token=config.bot_token)
dp = Dispatcher()

chat_router = Router()

@chat_router.message()
async def handle_message(message: types.Message):
    """
    LLM Chat Handler. This runs ONLY if no command handlers matched.
    """
    text = message.text.strip() if message.text else ""
    if not text:
        return

    log.info("User Message: %s", text)

    if text.startswith("!run "):
        command = text[len("!run "):]
        # We will execute the command directly here!
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

    task_manager = await TaskManager.create()

    dp["task_manager"] = task_manager
    
    dp.message.middleware(AuthMiddleware())

    dp.include_router(admin_router)
    dp.include_router(chat_router)

    log.info("Task manager and routers are initialized.")

    await reply_to_me("Termux agent is online.")

    llm_task = asyncio.create_task(llm_worker())
    polling_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(llm_task, polling_task)


if __name__ == "__main__":
    asyncio.run(main())
