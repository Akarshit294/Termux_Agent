import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from helpers import BOT_TOKEN, CHAT_ID, reply_to_me
# from llm_pipeline import run_llm_pipeline
# from health_check import run_health_check
# from bash_tool import execute_bash_command
from logger import get_logger

# Initialize it with the name of the current file
log = get_logger(__name__)

load_dotenv()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Only respond to YOUR messages — security filter
def is_authorized(message: types.Message) -> bool:
    return str(message.chat.id) == str(CHAT_ID)

@dp.message()
async def handle_message(message: types.Message):
    if not is_authorized(message):
        return  # Ignore anyone else messaging the bot

    text = message.text.strip()

    log.info("User Message: %s", text)

    # !run escape hatch — bypass LLM entirely
    if text.startswith("!run "):
        command = text[len("!run "):]
        await reply_to_me(f"⚡ Run command: `{command}`")
        # output = await execute_bash_command(command)
        # await reply_to_me(output)
        return

    # All other messages go through the LLM pipeline
    await reply_to_me("Thinking...")
    # await run_llm_pipeline(text)

# async def health_loop():
#     while True:
#         await asyncio.sleep(300)  # wait 5 minutes
#         await run_health_check()

async def main():
    log.info("MAIN STARTED!")
    await reply_to_me("Tablet assistant is online.")
    # health_task = asyncio.create_task(health_loop())
    polling_task = asyncio.create_task(dp.start_polling(bot))
    # await asyncio.gather(health_task, polling_task)
    await asyncio.gather(polling_task)

if __name__ == "__main__":
    asyncio.run(main())