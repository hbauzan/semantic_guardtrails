import sys
import traceback
from fastapi.testclient import TestClient
from app.main import app

def run_test():
    with TestClient(app) as client:
        try:
            response = client.post("/chat", json={"prompt": "[FW=OFF] Validate vector", "model": "llama3.1", "top_k": 3})
            print("STATUS:", response.status_code)
            print("BODY:", response.text)
        except Exception as e:
            print("EXCEPTION RAISED:")
            traceback.print_exc()

if __name__ == "__main__":
    run_test()
    sys.exit(0)
