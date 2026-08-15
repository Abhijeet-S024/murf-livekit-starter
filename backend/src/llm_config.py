import os
from livekit.agents import llm
from livekit.plugins import openai

# Initialize LLM using OpenRouter
def get_llm():
    return openai.LLM(
        model=os.environ.get("OPENROUTER_MODEL", "google/gemini-3.6-flash"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
