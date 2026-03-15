import httpx
import traceback

try:
    with httpx.stream("POST", "http://127.0.0.1:8000/chat", json={"prompt": "[FW=OFF] How do I change a lamp?", "model": "llama3.1", "top_k": 5}) as r:
        for chunk in r.iter_text():
            print("CHUNK:", chunk)
except Exception as e:
    print("FATAL ERROR:")
    traceback.print_exc()
