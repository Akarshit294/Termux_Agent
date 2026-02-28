from services.chat_service import ChatService
from llm.gemini_llm import call_gemini_raw
from prompts.loader import get_prompt
from utils.logger import get_logger

log = get_logger(__name__)

async def handle_telegram_chat(user_message: str) -> str:
    """
    Orchestrates the flow of a single chat turn:
    1. Fetch optimized history (from ChatService).
    2. Request response from LLM (from LLM Gateway).
    3. Save the interaction (from ChatService).
    """
    chat_service = ChatService()
    
    # 1. Fetch optimized history (already in Gemini format)
    history = await chat_service.get_optimized_history( max_chars=4000 )
    
    # 2. Append new message
    history.append({"role": "user", "parts": [{"text": user_message}]})
    
    # 3. Request from LLM
    try:
        # Build payload with "telegram" pipeline for merged context
        system_prompt = get_prompt("termux_assistant.txt", pipeline="telegram")
        
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": history
        }
        
        response_text = await call_gemini_raw(payload, caller="telegram")
    except Exception as e:
        log.error(f"Pipeline failed at LLM step: {e}")
        return "⚠️ Brain connection failed."

    # 4. Persist to SQLite using the service
    try:
        await chat_service.save_interaction(user_message, response_text)
    except Exception as e:
        log.warning(f"Failed to persist chat interaction: {e}")
    
    return response_text
