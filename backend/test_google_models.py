import os
from dotenv import load_dotenv
from google import genai

def list_models():
    load_dotenv("d:/Agent bharat26/murf-livekit-starter/backend/.env.local")
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    for model in client.models.list():
        print(model.name)

if __name__ == "__main__":
    list_models()
