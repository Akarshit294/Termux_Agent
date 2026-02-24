import asyncio
from helpers import reply_to_me

async def main():
    print("Sending Telegram message")
    await reply_to_me("This is the first message.")

asyncio.run(main())