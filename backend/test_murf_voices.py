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
    
    print("Fetching Murf Voices...")
    status, data = await check_murf_voices(api_key)
    print(f"Status: {status}")
    
    if status == 200:
        voices = data
        anisha_voices = [v for v in voices if "Anisha" in v.get("displayName", "")]
        nikhil_voices = [v for v in voices if "Nikhil" in v.get("displayName", "")]
        rachel_voices = [v for v in voices if "Rachel" in v.get("displayName", "")]
        print(f"Anisha voices: {anisha_voices}")
        print(f"Nikhil voices: {nikhil_voices}")
        print(f"Rachel voices: {rachel_voices}")
    else:
        print(f"Error: {data}")

if __name__ == "__main__":
    asyncio.run(main())
