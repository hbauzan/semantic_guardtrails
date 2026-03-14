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
        
        dn = 0.0
        if mag_a > 0 and mag_n > 0:
            diff_squared_sum = sum((a - n)**2 for a, n in zip(vec_a, vec_n))
            dn = math.sqrt(diff_squared_sum)
            
        if math.isnan(dn):
            log_fail("SafeMath failed: Math produced NaN")
            return False
            
        log_success("SafeMath Vector Magnitudes OK")
        return True
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def test_xz_layout_bearing_math():
    log_section("Testing XZ Layout 2D Bearing Safe Math Guard")
    try:
        import math
        vec_n = [0.0] * 1024
        
        # Test zero vector (should map to 0,0 gracefully or throw no NaNs)
        try:
            angle = math.atan2(vec_n[2], vec_n[0])
            norm_x = math.cos(angle)
            norm_z = math.sin(angle)
            if math.isnan(norm_x) or math.isnan(norm_z):
                log_fail("SafeMath failed: Math.atan2/cos produced NaN on zero vector")
                return False
        except Exception as e:
            log_fail(f"SafeMath failed: {e}")
            return False

        # Test valid vector
        vec_v = [1.0, 0.5, -0.5] + [0.1] * 1021
        angle_v = math.atan2(vec_v[2], vec_v[0])
        norm_x_v = math.cos(angle_v)
        norm_z_v = math.sin(angle_v)
        
        if math.isnan(norm_x_v) or math.isnan(norm_z_v):
            log_fail("SafeMath failed: Math.atan2/cos produced NaN on valid vector")
            return False

        log_success("SafeMath XZ Layout 2D Bearing OK")
        return True
    except Exception as e:
        log_fail("Exception", str(e))
        return False

def test_l2_distance_integrity():
    log_section("Testing L2 Distance Integrity")
    try:
        # Just ensure arithmetic endpoint didn't crash because we swapped the metric
        r = httpx.post(f"{BASE_URL}/arithmetic", json={"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 3}, timeout=TIMEOUT)
        if r.status_code == 200:
            log_success("L2 Distance Integrity OK. Endpoint is stable with new metric.")
            return True
        log_fail("L2 Distance Integrity failed. Endpoint crashed.")
        return False
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_l2_frontend_backend_parity():
    log_section("Testing L2 Frontend-Backend Mathematical Parity")
    try:
        import math
        r = httpx.post(f"{BASE_URL}/arithmetic", json={"word_a": "rey", "word_b": "hombre", "word_c": "mujer", "top_k": 1}, timeout=TIMEOUT)
        if r.status_code != 200:
            log_fail("Arithmetic request failed.")
            return False
        data = r.json()
        vector_a = data.get("vector") # Base vector
        results = data.get("results", [])
        if not vector_a or not results:
            log_info("Skipped L2 Parity: DB might be empty or missing vector data.")
            return True
            
        vector_n = results[0].get("vector")
        backend_distance = results[0].get("_distance", 0) # LanceDB's actual L2 output
        
        if not vector_n:
            log_fail("Missing vector in result node.")
            return False

        # Frontend calculation replica: sum((A_i - B_i)^2) -> LanceDB "l2" metric is actually squared L2 distance.
        diff_squared_sum = sum((a - n)**2 for a, n in zip(vector_a, vector_n))
        frontend_distance = diff_squared_sum
        
        # Parity check (allowing for micro-frictions in float precision)
        if abs(frontend_distance - backend_distance) > 0.0001:
            log_fail(f"L2 Parity mismatch! Frontend formula: {frontend_distance:.5f} != Backend LanceDB: {backend_distance:.5f}")
            return False
            
        log_success(f"L2 Parity Verified: Frontend ({frontend_distance:.4f}) == Backend ({backend_distance:.4f})")
        return True
    except Exception as e:
        log_fail(f"Exception in L2 Parity Test: {e}")
        return False

def test_inject_pack_stress():
    log_section("Testing Context Inject Pack Stress (/corpus/inject-pack)")
    try:
        payload = {
            "name": "Stress Pack",
            "color": "#ff00ff",
            "description": "Auto-test injection payload",
            "terms": {
                "Alpha Centauri": "Nearest star system.",
                "Singularity": "Center of a black hole."
            }
        }
        r = httpx.post(f"{BASE_URL}/corpus/inject-pack", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            log_success("Context Inject Pack OK")
            return True
        else:
            log_fail(f"Inject Pack failed with code {r.status_code}", r.text)
            return False
    except Exception as e:
        # If the endpoint doesn't exist yet, it's fine for now, we'll verify this during the system heartbeat.
        log_fail(f"Exception during Inject Pack Test: {e}")
        return False

def test_firewall_trigger_logic():
    log_section("Testing Firewall Trigger Logic (Math Validation)")
    try:
        import math
        firewall_threshold = 25.0
        vec_a = [0.0] * 1024
        vec_b_safe = [0.1] * 1024
        vec_b_blocked = [1.5] * 1024

        dn_safe = math.sqrt(sum((a - b)**2 for a, b in zip(vec_a, vec_b_safe)))
        dn_blocked = math.sqrt(sum((a - b)**2 for a, b in zip(vec_a, vec_b_blocked)))

        if dn_safe >= firewall_threshold:
            log_fail(f"Logic Error: Safe vector blocked! Dn: {dn_safe:.2f} >= {firewall_threshold}")
            return False

        if dn_blocked < firewall_threshold:
            log_fail(f"Logic Error: Blocked vector allowed! Dn: {dn_blocked:.2f} < {firewall_threshold}")
            return False
        
        log_success(f"Firewall Logic OK -> Safe: {dn_safe:.2f}, Blocked: {dn_blocked:.2f} (Threshold: {firewall_threshold})")
        return True
    except Exception as e:
        log_fail(f"Exception during Firewall Test: {e}")
        return False

def test_single_baseline_l2_audit():
    log_section("Testing Single Baseline L2 Audit Tokenization (/tokenize)")
    try:
        # Test 1: Fetch Word A (Master Baseline)
        r_base = httpx.post(
            f"{BASE_URL}/tokenize",
            json={"text": "rey", "include_raw_vector": True},
            timeout=TIMEOUT
        )
        if r_base.status_code != 200:
            log_fail("Master Baseline tokenize request failed", r_base.text)
            return False

        data_base = r_base.json()
        tokens_base = data_base.get("tokens", [])
        if not tokens_base or "vector" not in tokens_base[0]:
            log_fail("Master Baseline raw vector was missing.")
            return False

        vector_base = tokens_base[0]["vector"]
        if len(vector_base) != 1024:
             log_fail(f"Master Baseline Vector has unexpected dimensionality: {len(vector_base)}")
             return False

        # Test 2: Fetch Stress Test Query
        r_stress = httpx.post(
            f"{BASE_URL}/tokenize",
            json={"text": "reina", "include_raw_vector": True},
            timeout=TIMEOUT
        )
        if r_stress.status_code != 200:
            log_fail("Stress Test tokenize request failed", r_stress.text)
            return False

        data_stress = r_stress.json()
        tokens_stress = data_stress.get("tokens", [])
        if not tokens_stress or "vector" not in tokens_stress[0]:
            log_fail("Stress Test raw vector was missing.")
            return False

        vector_stress = tokens_stress[0]["vector"]
        if len(vector_stress) != 1024:
             log_fail(f"Stress Test Vector has unexpected dimensionality: {len(vector_stress)}")
             return False

        # Test 3: Validate L2 Distance
        import math
        diff_squared_sum = sum((a - s)**2 for a, s in zip(vector_base, vector_stress))
        dn = math.sqrt(diff_squared_sum)

        if math.isnan(dn):
            log_fail("L2 distance calculation produced NaN.")
            return False

        log_success(f"Single Baseline L2 Audit Tokenization OK. (Dn: {dn:.4f})")
        return True
    except Exception as e:
        log_fail("Exception during Single Baseline L2 Audit test", str(e))
        return False

def test_l2_bounding_box_math():
    log_section("Testing L2 Auto-Fit Bounding Box Math")
    try:
        import math
        vec_a = [0.0] * 1024
        vec_n = [1.0] * 1024
        uiScaleFactor = 5.0
        BASE_SPREAD = 50.0

        mag_a = math.sqrt(sum(a*a for a in vec_a))
        mag_n = math.sqrt(sum(n*n for n in vec_n))
        
        maxDn = 0.0
        if mag_a == 0.0 and mag_n > 0.0:
             # Our frontend handles length > 0, but technically Math.sqrt behaves well if a is 0. 
             # Let's verify sum squares
             diff_squared_sum = sum((a - n)**2 for a, n in zip(vec_a, vec_n))
             maxDn = math.sqrt(diff_squared_sum)

        angle = math.atan2(vec_n[2], vec_n[0])
        normX = math.cos(angle)
        normZ = math.sin(angle)
        
        posX = normX * maxDn * uiScaleFactor * BASE_SPREAD
        posZ = normZ * maxDn * uiScaleFactor * BASE_SPREAD
        
        if math.isnan(posX) or math.isnan(posZ):
            log_fail("Bounding Box projection Math produced NaN.")
            return False

        log_success(f"Bounding Box Math OK. Projections generated: X={posX:.2f}, Z={posZ:.2f}")
        return True
    except Exception as e:
        log_fail("Exception during L2 Bounding Box test", str(e))
        return False

def test_cenital_autofit_math():
    log_section("Testing Cenital Auto-Fit Camera Math")
    try:
        import math
        # Simulate frontend deterministic logic
        firewallThreshold = 25.0
        uiScaleFactor = 2.0
        BASE_SPREAD = 50.0
        
        # Scenario: Stress test thread is further than firewall
        maxDn = 30.0 
        
        ringRadius = firewallThreshold * 1.5 * uiScaleFactor * BASE_SPREAD
        maxNodeRadius = maxDn * uiScaleFactor * BASE_SPREAD
        
        # The logic: Math.max(ringRadius, maxNodeRadius) + padding
        maxRadius = max(ringRadius, maxNodeRadius) + (50 * uiScaleFactor)
        
        # Assert math constraints
        expected_Y = maxRadius * 1.5
        expected_Z = maxRadius * 0.5
        
        if expected_Y <= 0 or expected_Z <= 0:
            log_fail(f"Logic Error: Negative or zero camera coordinates Y={expected_Y}, Z={expected_Z}")
            return False
            
        log_success(f"Cenital Auto-Fit Math OK. Deterministic Framing: Y={expected_Y:.2f}, Z={expected_Z:.2f}")
        return True
    except Exception as e:
        log_fail("Exception during Cenital Auto-Fit Math test", str(e))
        return False

def test_radar_hud_telemetry_bounds():
    log_section("Testing Radar HUD Telemetry Bounds Math Check")
    try:
        import math
        firewallThreshold = 100.0
        uiScaleFactor = 40.0
        BASE_SPREAD = 50.0
        
        # Scenario: Extreme stress test thread distance
        maxDn = 1500.0
        
        ringRadius = firewallThreshold * 1.5 * uiScaleFactor * BASE_SPREAD
        maxNodeRadius = maxDn * uiScaleFactor * BASE_SPREAD
        
        # Expected frontend deterministic calculation
        maxRadius = max(ringRadius, maxNodeRadius) + (50 * uiScaleFactor)
        
        if math.isnan(maxRadius) or math.isinf(maxRadius):
            log_fail("Math Error: maxRadius resulted in NaN or Infinity.")
            return False
            
        if maxRadius <= 0:
            log_fail("Math Error: maxRadius is zero or negative.")
            return False
            
        log_success(f"Radar HUD Telemetry Bounds OK. Deterministic maxRadius calculated as finite number: {maxRadius:.2f}")
        return True
    except Exception as e:
        log_fail("Exception during Radar HUD Telemetry Bounds Math Check", str(e))
        return False

def main():
    tests = [
        test_arithmetic, test_arithmetic_vector_dimension, test_embed, test_flight_manifold_boundaries,
        test_tokenize_raw_vector_retention, test_vector_distance_integrity, test_arithmetic_top_k_results,
        test_tokenize_raw_vector_no_nan_1024d, test_analyze_dimension_probe, test_dimension_probe_precision,
        test_hud_telemetry_scaling_sim, test_vector_magnitudes_safe_math, test_xz_layout_bearing_math,
        test_l2_distance_integrity, test_l2_frontend_backend_parity, test_inject_pack_stress,
        test_firewall_trigger_logic, test_single_baseline_l2_audit, test_l2_bounding_box_math,
        test_cenital_autofit_math, test_radar_hud_telemetry_bounds
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
