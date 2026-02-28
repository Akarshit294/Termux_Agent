import asyncio
import aiohttp
from utils.config import config
from utils.logger import get_logger

log = get_logger(__name__, process_name="supervisor")


groq_lock = asyncio.Lock()
GROQ_MODEL = "openai/gpt-oss-20b" 


def simple_backoff(max_retries=3):
    """A lightweight decorator strictly for exponential backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    log.warning(f"[Groq] Network/Rate limit error: {e}. Retrying in {wait_time}s... ({attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
            
            log.error("[Groq] Max retries exceeded.")
            raise Exception("Groq API failed after maximum retries.")
        return wrapper
    return decorator


@simple_backoff(max_retries=3)
async def call_groq_locked(payload: dict) -> str:
    """
    Executes the Groq API call safely. 
    """
    if not config.groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.groq_api_key.get_secret_value()}",
        "Content-Type": "application/json"
    }
    
    payload["model"] = GROQ_MODEL
    
    async with groq_lock:
        log.info("[Groq] Lock acquired. Sending request...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        content = data["choices"][0]["message"]["content"]
                    except (KeyError, IndexError, TypeError) as e:
                        log.error("Unexpected response shape: %s", data)
                        raise Exception("Unexpected response format") from e

                    log.info(f"GROQ Response: {content}")
                    return content

                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")
