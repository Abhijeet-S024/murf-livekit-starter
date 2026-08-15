import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def check_murf_voices(api_key):
    url = "https://api.murf.ai/v1/speech/voices"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return resp.status, await resp.json()

async def main():
    load_dotenv("d:/Agent bharat26/murf-livekit-starter/backend/.env.local")
    api_key = os.getenv("MURF_API_KEY")
    
    status, data = await check_murf_voices(api_key)
    
    if status == 200:
        voices = data
        with open("d:/Agent bharat26/murf-livekit-starter/backend/murf_voices.txt", "w", encoding="utf-8") as f:
            for v in voices:
                f.write(f"VoiceId: {v.get('voiceId')}, Name: {v.get('displayName')}, Locale: {v.get('locale')}\n")
        print("Voices written to murf_voices.txt")
    else:
        print(f"Error: {data}")

if __name__ == "__main__":
    asyncio.run(main())
