import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            
            print("🚀 Available Text Generation Models:\n")
            for model in data.get("models", []):
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    # Strips the "models/" prefix for easier reading
                    print(f"✅ {model['name'].replace('models/', '')}")

if __name__ == "__main__":
    asyncio.run(list_models())