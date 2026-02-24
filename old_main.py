import asyncio
from helpers import reply_to_me
from logger import get_logger

# Initialize it with the name of the current file
log = get_logger(__name__)

async def main():
    log.info("Sending Telegram message")
    await reply_to_me("This is the 12th message.")

asyncio.run(main())