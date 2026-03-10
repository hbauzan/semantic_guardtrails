import httpx
import sys
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10.0

def log_section(msg): print(f"\\n--- {msg} ---")
def log_info(msg): print(f"ℹ️ {msg}")
def log_success(msg): print(f"✅ {msg}")
def log_fail(msg, detail=""): print(f"❌ {msg} {detail}")

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
def test_flight_manifold_boundaries():
    log_section("Testing Flight Manifold Boundaries (/galaxy)")
    try:
        response = httpx.get(f"{BASE_URL}/galaxy", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if not data:
                log_info("Skipped: Database is empty.")
                return True
            
            out_of_bounds = 0
            for item in data[:100]: # Check sample
                if 'xyz' in item:
                    xyz = item['xyz']
                    if not all(0 <= c <= 300 for c in xyz):
                        out_of_bounds += 1
            
            if out_of_bounds == 0:
                log_success("Flight Manifold Check: All coordinates within [0, 300] safe flight zone.")
                return True
            else:
                log_fail(f"Flight Hazard: {out_of_bounds} nodes outside [0, 300] boundaries.")
                return False
        else:
            log_fail("Galaxy request failed", response.text)
            return False
    except Exception as e:
        log_fail("Exception during flight manifold test", str(e))
        return False

def main():
    tests = [test_arithmetic, test_embed, test_flight_manifold_boundaries]
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    if all_passed:
        print("✅ ALL SYSTEMS GO")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
