import httpx
from decouple import config

OLLAMA_API = config("OLLAMA_API", default="http://localhost:11434/api/generate")

async def get_ollama_response(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_API, json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        })

    if response.status_code != 200:
        raise Exception("Error communicating with Ollama")

    ollama_response = response.json()
    return ollama_response["response"]