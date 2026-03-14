import httpx
import json
from typing import AsyncGenerator

class ChatService:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.client = httpx.AsyncClient(timeout=300.0)

    async def stream_chat(self, model: str, prompt: str, context: str = "") -> AsyncGenerator[str, None]:
        
        system_prompt = "You are a helpful AI assistant. Answer based on the provided CONTEXT. If the context does not contain the answer, say you don't know."
        full_prompt = f"CONTEXT:\n{context}\n\nUSER PROMPT:\n{prompt}" if context else prompt
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "system": system_prompt,
            "stream": True
        }
        try:
            async with self.client.stream("POST", f"{self.ollama_host}/api/generate", json=payload) as response:
                if response.status_code != 200:
                    yield json.dumps({"error": f"Ollama HTTP {response.status_code}"}) + "\n"
                    return

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            yield f"Error connecting to Ollama: {str(e)}"
