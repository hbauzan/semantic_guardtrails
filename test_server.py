import sys
import traceback
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("Starting test...")
try:
    response = client.post("/chat", json={"prompt": "[FW=OFF] How do I change a lamp?", "model": "llama3.1", "top_k": 5})
    print("Status:", response.status_code)
    print("Body:", response.text)
except Exception as e:
    traceback.print_exc()
