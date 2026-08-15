import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def check_murf_generate(api_key):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {"voiceId": "en-IN-isha", "text": "Hello, how can I help you?", "format": "MP3"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            return resp.status, await resp.text()

async def main():
    load_dotenv("d:/Agent bharat26/murf-livekit-starter/backend/.env.local")
    api_key = os.getenv("MURF_API_KEY")
    
    print("Testing Murf Generate API Key...")
    status, text = await check_murf_generate(api_key)
    print(f"Status: {status}")
    print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(main())
