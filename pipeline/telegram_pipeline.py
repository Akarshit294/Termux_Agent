from services.chat_service import ChatService
from llm.gemini_llm import call_gemini
from utils.logger import get_logger

log = get_logger(__name__)

async def handle_telegram_chat(user_message: str) -> str:
    """
    Orchestrates the flow of a single chat turn:
    1. Fetch optimized history (from ChatService).
    2. Request response from LLM (Agent Loop).
    3. Save the interaction.
    """
    chat_service = ChatService()
    
    # 1. Fetch optimized history
    history = await chat_service.get_optimized_history(max_chars=4000)
    
    # 2. Append new message to history
    history.append({"role": "user", "parts": [{"text": user_message}]})
    
    # 3. Request from LLM (the agent loop handles thinking/acting)
    try:
        # Wrap in payload for call_gemini (the decorated orchestrator)
        # Note: call_gemini expects 'payload' and 'caller' as per @llm_gateway
        payload = {
            "history": history,
            "caller": "telegram"
        }
        
        response_text = await call_gemini(payload, caller="telegram")
    except Exception as e:
        log.error(f"Pipeline failed at LLM step: {e}")
        return "⚠️ Brain connection failed."

    # 4. Persist to SQLite using the service
    try:
        await chat_service.save_interaction(user_message, response_text)
    except Exception as e:
        log.warning(f"Failed to persist chat interaction: {e}")
    
    return response_text
