import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def check_murf_generate(api_key, voice_id, model="GEN2"):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {"voiceId": voice_id, "text": "Hello, how can I help you?", "format": "MP3", "modelVersion": model, "style": "Conversational"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            return resp.status, await resp.text()

async def main():
    load_dotenv("d:/Agent bharat26/murf-livekit-starter/backend/.env.local")
    api_key = os.getenv("MURF_API_KEY")
    
    for voice_id in ["en-IN-nikhil", "Nikhil", "en-IN-Nikhil", "en-IN-anisha", "Anisha"]:
        print(f"Testing Voice ID: {voice_id}")
        status, text = await check_murf_generate(api_key, voice_id)
        print(f"Status: {status}")
        if status != 200:
            print(f"Response: {text[:200]}")
        else:
            print("Success!")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
