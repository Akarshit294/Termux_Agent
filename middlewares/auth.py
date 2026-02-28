from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Any, Callable, Dict, Awaitable
from utils.config import config

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Check if the incoming message is from the authorized CHAT_ID
        if int(event.chat.id) != config.chat_id:
            return # Silently ignore unauthorized users
        
        return await handler(event, data)
