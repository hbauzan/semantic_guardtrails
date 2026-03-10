import httpx
import sys
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10.0

def test_arithmetic():
    print("Testing /arithmetic...")
    payload = {"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 3}
    try:
        r = httpx.post(f"{BASE_URL}/arithmetic", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            print("✅ Arithmetic OK")
            return True
        print(f"❌ Failed: {r.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_embed():
    print("Testing /embed...")
    try:
        r = httpx.post(f"{BASE_URL}/embed", json={"text": "test"}, timeout=TIMEOUT)
        if r.status_code == 200:
            print("✅ Embed OK")
            return True
        print("❌ Failed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_arithmetic() and test_embed():
        print("✅ ALL SYSTEMS GO")
        sys.exit(0)
    sys.exit(1)
