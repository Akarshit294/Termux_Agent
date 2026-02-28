from database import telegram_db
from database.models import ChatMessage
from utils.logger import get_logger

log = get_logger(__name__)

class ChatService:
    def __init__(self):
        pass

    async def get_optimized_history(self, max_chars: int = 4000):
        """
        Fetches history from the repository and trims it based on character count.
        Returns history in the format expected by the Gemini API.
        """
        all_history = await telegram_db.get_telegram_history(limit=50) 
        
        optimized = []
        current_chars = 0
        
        # Iterate backwards (newest first) and stop when full
        for msg in reversed(all_history):
            if current_chars + len(msg.text_content) > max_chars:
                break
            
            optimized.insert(0, {
                "role": msg.role,
                "parts": [{"text": msg.text_content}]
            })
            current_chars += len(msg.text_content)
            
        log.info(f"Optimized history to {len(optimized)} messages (~{current_chars} chars).")
        return optimized

    async def save_interaction(self, user_text: str, model_text: str):
        """
        Persists both the user message and the model's response to the database.
        """
        await telegram_db.save_telegram_message(ChatMessage(role="user", text_content=user_text))
        await telegram_db.save_telegram_message(ChatMessage(role="model", text_content=model_text))
        log.info("Interaction saved to database.")
