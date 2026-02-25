import aiohttp
from helpers import GEMINI_API_KEY
from logger import get_logger
from .llm_gateway import llm_gateway


log = get_logger(__name__, process_name = "gemini")

@llm_gateway
async def call_gemini_raw(payload: dict) -> str:
    """
    Takes a strict Gemini JSON payload and returns the text response.
    Throws an exception if anything goes wrong.
    """
    log.info(f"Making a Gemini call for this Input: {payload}")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:

            if response.status == 200:
                data = await response.json()
                res = data["candidates"][0]["content"]["parts"][0]["text"]
                log.info(f"Output: {res}")
                return res
            
            # If it is a 429, 500, or 400, we instantly raise an error.
            error_text = await response.text()
            log.warning(f"Output Error: {error_text}")
            raise Exception(f"HTTP {response.status}: {error_text}")