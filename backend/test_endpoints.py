import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def check_deepgram(api_key):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Token {api_key}"}
        async with session.get("https://api.deepgram.com/v1/projects", headers=headers) as resp:
            return resp.status, await resp.text()

async def check_google(api_key):
    # Just check a simple endpoint for Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return resp.status, (await resp.text())[:100]

async def check_murf(api_key):
    # Check murf voice list or something. Wait, the LiveKit plugin probably uses a specific URL.
    # Let's check LiveKit Murf plugin documentation or simply test with a common endpoint.
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {"voiceId": "en-US-rachel", "text": "test"}
    # The endpoint might be different. Let's just try to hit it and see if we get unauthorized or bad request.
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            return resp.status, (await resp.text())[:100]

async def main():
    load_dotenv("d:/Agent bharat26/murf-livekit-starter/backend/.env.local")
    
    print("Testing Deepgram API Key...")
    dg_status, dg_resp = await check_deepgram(os.getenv("DEEPGRAM_API_KEY"))
    print(f"Deepgram: {dg_status}")
    
    print("Testing Google API Key...")
    google_status, google_resp = await check_google(os.getenv("GOOGLE_API_KEY"))
    print(f"Google: {google_status}")
    
    print("Testing Murf API Key...")
    murf_status, murf_resp = await check_murf(os.getenv("MURF_API_KEY"))
    print(f"Murf: {murf_status} - {murf_resp}")

if __name__ == "__main__":
    asyncio.run(main())
