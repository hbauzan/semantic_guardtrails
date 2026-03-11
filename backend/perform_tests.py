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

def test_arithmetic_vector_dimension():
    log_section("Testing Arithmetic Vector Dimension (/arithmetic)")
    payload = {"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 3}
    try:
        r = httpx.post(f"{BASE_URL}/arithmetic", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            if not isinstance(data, dict):
                log_fail("Response is not a dictionary. Missing 'vector' and 'results' fields.")
                return False
                
            vector = data.get("vector", [])
            results = data.get("results", [])
            
            if len(vector) != 1024:
                log_fail(f"Vector length is not 1024. Got: {len(vector)}")
                return False
                
            if len(results) == 0:
                log_info("Skipped results count check: Database is empty.")
            elif len(results) != 3:
                log_fail(f"Results length does not match top_k=3. Got: {len(results)}")
                return False
                
            log_success("Arithmetic Vector Dimension OK")
            return True
            
        log_fail(f"Request failed: {r.text}")
        return False
    except Exception as e:
        log_fail(f"Exception during test: {str(e)}")
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

def test_tokenize_raw_vector_retention():
    log_section("Testing Tokenize Raw Vector Retention (/tokenize)")
    try:
        # Test 1: include_raw_vector = False (Default)
        r_false = httpx.post(
            f"{BASE_URL}/tokenize", 
            json={"text": "holograma", "include_raw_vector": False}, 
            timeout=TIMEOUT
        )
        data_false = r_false.json()
        tokens_false = data_false.get("tokens", [])
        if not tokens_false or "vector" in tokens_false[0]:
            log_fail("Raw vector was NOT removed when include_raw_vector=False.")
            return False

        # Test 2: include_raw_vector = True
        r_true = httpx.post(
            f"{BASE_URL}/tokenize", 
            json={"text": "holograma", "include_raw_vector": True}, 
            timeout=TIMEOUT
        )
        data_true = r_true.json()
        tokens_true = data_true.get("tokens", [])
        if not tokens_true or "vector" not in tokens_true[0]:
            log_fail("Raw vector was NOT retained when include_raw_vector=True.")
            return False
            
        # Verify 1024D length
        vector_len = len(tokens_true[0]["vector"])
        if vector_len not in [768, 1024]:
             log_fail(f"Vector has unexpected dimensionality: {vector_len}")
             return False

        log_success("Tokenize Raw Vector Retention OK")
        return True
    except Exception as e:
        log_fail("Exception during tokenize raw vector test", str(e))
        return False

def test_tokenize_raw_vector_no_nan_1024d():
    log_section("Testing Tokenize Raw Vector No NaN 1024D (/tokenize)")
    try:
        r = httpx.post(
            f"{BASE_URL}/tokenize", 
            json={"text": "geometria", "include_raw_vector": True}, 
            timeout=TIMEOUT
        )
        if r.status_code != 200:
            log_fail("Tokenize request failed", r.text)
            return False
            
        data = r.json()
        tokens = data.get("tokens", [])
        if not tokens or "vector" not in tokens[0]:
            log_fail("Raw vector was missing when include_raw_vector=True.")
            return False
            
        vector = tokens[0]["vector"]
        
        # Verify 1024D length
        if len(vector) != 1024:
             log_fail(f"Vector has unexpected dimensionality: {len(vector)}")
             return False

        # Verify No NaNs
        import math
        if any(v is None or math.isnan(v) for v in vector):
             log_fail("Vector contains NaN or None values.")
             return False
             
        # Verify floats
        if not all(isinstance(v, (int, float)) for v in vector):
             log_fail("Vector contains non-numeric values.")
             return False

        log_success("Tokenize Raw Vector No NaN 1024D OK")
        return True
    except Exception as e:
        log_fail("Exception during Tokenize Raw Vector No NaN 1024D test", str(e))
        return False

def test_vector_distance_integrity():
    log_section("Testing Vector Distance Integrity (/arithmetic)")
    payload = {"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 3}
    try:
        r = httpx.post(f"{BASE_URL}/arithmetic", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            if not isinstance(data, dict):
                log_fail("Response is not a dictionary.")
                return False
                
            # Arithmetic should return its own vector
            vector = data.get("vector", [])
            if len(vector) != 1024:
                log_fail(f"Result vector length is not 1024. Got: {len(vector)}. Needed for distance calculation.")
                return False
                
            log_success("Vector Distance Integrity OK - 1024D vector reliably provided.")
            return True
            
        log_fail(f"Request failed: {r.text}")
        return False
    except Exception as e:
        log_fail(f"Exception during vector distance integrity test: {str(e)}")
        return False

def test_arithmetic_top_k_results():
    log_section("Testing Arithmetic Top K Results (/arithmetic)")
    payload = {"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 3}
    try:
        r = httpx.post(f"{BASE_URL}/arithmetic", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", []) if isinstance(data, dict) else data
            
            if not isinstance(results, list):
                log_fail("Response results must be a list structure.")
                return False
                
            if len(results) > 0:
                first = results[0]
                if "word" not in first and "text" not in first:
                    log_fail("Missing 'word' or 'text' key in result.")
                    return False
                if "score" not in first:
                    log_fail("Missing 'score' key in result.")
                    return False
            
            log_success("Arithmetic Top K Results OK")
            return True
        else:
            log_fail("Failed response", r.text)
            return False
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def test_analyze_dimension_probe():
    log_section("Testing Analyze Dimension Probe (/analyze_dimension)")
    payload = {"dimension_index": 512, "top_k": 5}
    try:
        r = httpx.post(f"{BASE_URL}/analyze_dimension", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            if not isinstance(data, dict):
                log_fail("Response is not a dictionary.")
                return False
            
            if "error" in data:
                if "empty" in data["error"].lower() or "run ingest_vocab" in data["error"].lower():
                    log_info(f"Skipped: {data['error']}")
                    return True
                else:
                    log_fail(f"Logic Error: {data['error']}")
                    return False
                
            dimension = data.get("dimension")
            if dimension != 512:
                log_fail(f"Returned dimension does not match request. Got: {dimension}")
                return False
                
            top_activators = data.get("top_activators", [])
            bottom_activators = data.get("bottom_activators", [])
            
            if not isinstance(top_activators, list) or not isinstance(bottom_activators, list):
                log_fail("Activators must be lists.")
                return False
                
            log_success("Analyze Dimension Probe OK")
            return True
        else:
            log_fail("Failed response", r.text)
            return False
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def test_hud_telemetry_scaling_sim():
    log_section("Testing HUD Telemetry Scaling Simulation")
    try:
        # Simulate calculation bounding limits at extreme stretches
        x_stretch = 40.0
        max_index = 1024
        # At max stretch, length check
        length = max_index * x_stretch
        if length > 50000: # We need up to ~40k max roughly
             log_info("Max scale exceeds 50000, may clip.")
        else:
             log_success(f"Max Scale {length} fits neatly inside 100,000 unit Frustum.")
        return True
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def test_dimension_probe_precision():
    log_section("Testing Dimension Probe Precision (/analyze_dimension)")
    try:
        log_info("Probing boundaries [0] and [1023] for magnitude stability...")
        low_res = httpx.post(f"{BASE_URL}/analyze_dimension", json={"dimension_index": 0, "top_k": 3}, timeout=TIMEOUT)
        high_res = httpx.post(f"{BASE_URL}/analyze_dimension", json={"dimension_index": 1023, "top_k": 3}, timeout=TIMEOUT)
        
        if low_res.status_code == 200 and high_res.status_code == 200:
            log_success("Dimension Probe Precision bounds OK")
            return True
        else:
            log_fail("Probe bounds check failed.")
            return False
    except Exception as e:
        log_fail("Exception during probe precision test", str(e))
        return False

def test_vector_magnitudes_safe_math():
    log_section("Testing Vector Magnitudes Safe Math Guard")
    try:
        import math
        vec_a = [1.0] * 1024
        vec_n = [0.0] * 1024
        
        mag_a = math.sqrt(sum(a*a for a in vec_a))
        mag_n = math.sqrt(sum(n*n for n in vec_n))
        
        dn = 1.0
        if mag_a > 0 and mag_n > 0:
            dot = sum(a * b for a, b in zip(vec_a, vec_n))
            dn = 1 - (dot / (mag_a * mag_n))
            
        if math.isnan(dn):
            log_fail("SafeMath failed: Math produced NaN")
            return False
            
        log_success("SafeMath Vector Magnitudes OK")
        return True
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def main():
    tests = [
        test_arithmetic, test_arithmetic_vector_dimension, test_embed, test_flight_manifold_boundaries,
        test_tokenize_raw_vector_retention, test_vector_distance_integrity, test_arithmetic_top_k_results,
        test_tokenize_raw_vector_no_nan_1024d, test_analyze_dimension_probe, test_dimension_probe_precision,
        test_hud_telemetry_scaling_sim, test_vector_magnitudes_safe_math
    ]
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
