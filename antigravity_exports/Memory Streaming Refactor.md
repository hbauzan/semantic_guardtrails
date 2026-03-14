# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

# SYSTEM DIRECTIVE: SSA PROTOCOL V18 - MEMORY STREAMING & HARD RESOURCE CAP

**ROLE**: Senior Systems Engineer / Performance Architect.
**MISSION**: Eradicate the severe memory leak and CPU bottleneck during PDF ingestion. Transition the architecture from "Batch Processing" to "Page-by-Page Streaming" to keep RAM usage strictly under 4GB and prevent macOS memory compression on M4 Pro architectures.

## 1. BACKEND: GENERATOR-BASED STREAMING REFACTOR
* **Dependency Injection**: Add `psutil` to `backend/requirements.txt`.
* **Iterator Pattern (`app/modules/ingestor.py`)**: 
    * Refactor `load_file` and `_load_pdf` to return a `Generator` (`yield`), NOT a `List`. 
    * Do not accumulate chunks in memory. Yield them page by page.
* **Processing Loop (`app/api/routes.py` -> `process_pdf_background`)**:
    * Consume the generator. Since `total_chunks` is unknown upfront in a stream, change the progress tracking to rely on `processed_chunks` dynamically, or do a fast metadata pass to get `total_pages` via `fitz`.
    * Vectorize, insert to LanceDB, and IMMEDIATELY discard the batch.
    * Explicitly call `del` on processed objects and `gc.collect()` periodically.
* **RSS Hard Cap Monitor**: 
    * Implement a check using `psutil.Process().memory_info().rss`. 
    * If the process RAM exceeds 4GB (4 * 1024 * 1024 * 1024 bytes), terminate the task immediately, log a critical warning, and set the task status to `'CRITICAL_MEMORY_ABORT'`.

## 2. FRONTEND & API: RAM TELEMETRY
* **API (`routes.py`)**: Add a `ram_usage_mb` field to the `/corpus/task-status/{task_id}` endpoint response.
* **State (`store.ts`)**: Add `ramUsageMb` (number) to the Zustand store.
* **UI (`ArithmeticHUD.tsx`)**: 
    * Display "Worker RAM: [X] MB" in the Context Injector modal during active processing.
    * Handle the `'CRITICAL_MEMORY_ABORT'` status gracefully, showing a red warning to the user.

## 3. SCRIPT UPDATES & EXECUTION
* **`run_server.sh` & `run_tests.sh`**: Ensure these scripts automatically install new dependencies (e.g., `pip install -r requirements.txt` or similar safeguard) before booting, so `psutil` doesn't crash the boot sequence.
* **Execution Mandate**: After implementing the code, you MUST execute `run_tests.sh` and `run_server.sh` to verify that the system boots and the tests pass without hanging.

## 4. DOCUMENTATION LOOP (MANDATORY)
Every functional change MUST be accompanied by:
1. An update to `manifest.json`: Add `"streaming_ingestion": true` and `"hard_memory_cap": true` to `active_features`.
2. An update to `architecture_spec.md`: Update Section 4 (Knowledge Ingestion) to reflect the Generator-based streaming architecture, `psutil` telemetry, and the 4GB Hard RAM Cap.

## 5. TESTING SOVEREIGNTY (MANDATORY)
`backend/perform_tests.py` is the System Heartbeat. Because we are changing the ingestion logic and adding telemetry, you MUST add the following specific test functions to `perform_tests.py`:
1. `test_task_status_ram_telemetry()`: Mock a task and verify that `/corpus/task-status/{task_id}` returns the `ram_usage_mb` field.
2. `test_streaming_ingestor_generator()`: Verify that `Ingestor.load_file` returns a generator type, not a list, ensuring the stream architecture is intact.

**OUTPUT FORMAT**: Provide the exact surgical code edits required for each file. Do not rewrite entire files unless absolutely necessary.

*Edited relevant file*

*Grep searched codebase*

*Viewed [ingestor.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/modules/ingestor.py) *

*Viewed [routes.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/api/routes.py) *

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Viewed [store.ts](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/store.ts) *

*Viewed [ArithmeticHUD.tsx](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/components/ArithmeticHUD.tsx) *

*Viewed [run_server.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_server.sh) *

*Viewed [run_tests.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_tests.sh) *

*Viewed [manifest.json](file:///Users/hbauzan/treepwood/semantic_guardtrails/manifest.json) *

*Viewed [architecture_spec.md](file:///Users/hbauzan/treepwood/semantic_guardtrails/architecture_spec.md) *

*Viewed [requirements.txt](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt) *

*Viewed [ArithmeticHUD.tsx](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/components/ArithmeticHUD.tsx) *

*Edited relevant file*

### User Input

This is a system-generated message that is sent due to the user's review policy. Proceed with the decision that you think is the most optimal here.

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `./run_tests.sh`*

*User accepted the command `./run_server.sh`*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*User accepted the command `python3 backend/perform_tests.py`*

*Checked command status*

*User accepted the command `./run_server.sh`*

*Checked command status*

*User accepted the command `./run_tests.sh`*

*Checked command status*

*Checked command status*

*Edited relevant file*

*Edited relevant file*

### User Input

Bueno titán, a ver si te pones las pilas la reconcha de tu madre que me vas a dejar re loco, mirá que tiene que salir HOY ESTO TIENE QUE QUEDAR HOY SINO ME VOY A REQUEMAR!!!

MIRÁ MIRÁ CARAJO TODOS ESOS ERRORES EN LOS TESTS, QUE PAS??? no hiciste lso tste?=?=?

(sg_env) hbauzan ~/treepwood/semantic_guardtrails [real_tests] $ ./run_tests.sh
🧹 Clearing Vite and Build caches...
👁️ Deep Observability Testing Initialized.
🤖 Checking Sovereign Ollama Motor...
🔍 Checking Ollama Motor Status...
✅ Ollama is RUNNING.
Requirement already satisfied: fastapi>=0.109.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 1)) (0.135.1)
Requirement already satisfied: uvicorn>=0.27.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 2)) (0.41.0)
Requirement already satisfied: pydantic>=2.6.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 3)) (2.12.5)
Requirement already satisfied: pydantic-settings>=2.1.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 4)) (2.13.1)
Requirement already satisfied: sentence-transformers>=2.3.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (5.2.3)
Requirement already satisfied: lancedb>=0.5.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 6)) (0.29.2)
Requirement already satisfied: numpy>=1.26.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 7)) (2.4.3)
Requirement already satisfied: umap-learn>=0.5.5 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 8)) (0.5.11)
Requirement already satisfied: orjson>=3.9.10 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 9)) (3.11.7)
Requirement already satisfied: python-multipart>=0.0.9 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 10)) (0.0.22)
Requirement already satisfied: torch>=2.1.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (2.10.0)
Requirement already satisfied: pyarrow>=15.0.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 12)) (23.0.1)
Requirement already satisfied: xxhash>=3.4.1 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 13)) (3.6.0)
Requirement already satisfied: scikit-learn>=1.4.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 14)) (1.8.0)
Requirement already satisfied: joblib>=1.3.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 15)) (1.5.3)
Requirement already satisfied: tqdm>=4.66.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 16)) (4.67.3)
Requirement already satisfied: pandas>=2.0.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 17)) (3.0.1)
Requirement already satisfied: pylance>=0.10.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 18)) (2.0.1)
Requirement already satisfied: plotly>=5.18.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 19)) (6.6.0)
Requirement already satisfied: rich>=13.0.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 20)) (14.3.3)
Requirement already satisfied: pymupdf>=1.23.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 21)) (1.27.2)
Requirement already satisfied: psutil>=5.9.0 in ./sg_env/lib/python3.14/site-packages (from -r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 22)) (7.2.2)
Requirement already satisfied: starlette>=0.46.0 in ./sg_env/lib/python3.14/site-packages (from fastapi>=0.109.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 1)) (0.52.1)
Requirement already satisfied: typing-extensions>=4.8.0 in ./sg_env/lib/python3.14/site-packages (from fastapi>=0.109.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 1)) (4.15.0)
Requirement already satisfied: typing-inspection>=0.4.2 in ./sg_env/lib/python3.14/site-packages (from fastapi>=0.109.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 1)) (0.4.2)
Requirement already satisfied: annotated-doc>=0.0.2 in ./sg_env/lib/python3.14/site-packages (from fastapi>=0.109.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 1)) (0.0.4)
Requirement already satisfied: click>=7.0 in ./sg_env/lib/python3.14/site-packages (from uvicorn>=0.27.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 2)) (8.3.1)
Requirement already satisfied: h11>=0.8 in ./sg_env/lib/python3.14/site-packages (from uvicorn>=0.27.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 2)) (0.16.0)
Requirement already satisfied: annotated-types>=0.6.0 in ./sg_env/lib/python3.14/site-packages (from pydantic>=2.6.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 3)) (0.7.0)
Requirement already satisfied: pydantic-core==2.41.5 in ./sg_env/lib/python3.14/site-packages (from pydantic>=2.6.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 3)) (2.41.5)
Requirement already satisfied: python-dotenv>=0.21.0 in ./sg_env/lib/python3.14/site-packages (from pydantic-settings>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 4)) (1.2.2)
Requirement already satisfied: transformers<6.0.0,>=4.41.0 in ./sg_env/lib/python3.14/site-packages (from sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (5.3.0)
Requirement already satisfied: huggingface-hub>=0.20.0 in ./sg_env/lib/python3.14/site-packages (from sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (1.6.0)
Requirement already satisfied: scipy in ./sg_env/lib/python3.14/site-packages (from sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (1.17.1)
Requirement already satisfied: packaging>=20.0 in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (26.0)
Requirement already satisfied: pyyaml>=5.1 in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (6.0.3)
Requirement already satisfied: regex!=2019.12.17 in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (2026.2.28)
Requirement already satisfied: tokenizers<=0.23.0,>=0.22.0 in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (0.22.2)
Requirement already satisfied: typer in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (0.24.1)
Requirement already satisfied: safetensors>=0.4.3 in ./sg_env/lib/python3.14/site-packages (from transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (0.7.0)
Requirement already satisfied: filelock>=3.10.0 in ./sg_env/lib/python3.14/site-packages (from huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (3.25.1)
Requirement already satisfied: fsspec>=2023.5.0 in ./sg_env/lib/python3.14/site-packages (from huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (2026.2.0)
Requirement already satisfied: hf-xet<2.0.0,>=1.3.2 in ./sg_env/lib/python3.14/site-packages (from huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (1.3.2)
Requirement already satisfied: httpx<1,>=0.23.0 in ./sg_env/lib/python3.14/site-packages (from huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (0.28.1)
Requirement already satisfied: anyio in ./sg_env/lib/python3.14/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (4.12.1)
Requirement already satisfied: certifi in ./sg_env/lib/python3.14/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (2026.2.25)
Requirement already satisfied: httpcore==1.* in ./sg_env/lib/python3.14/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (1.0.9)
Requirement already satisfied: idna in ./sg_env/lib/python3.14/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.20.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (3.11)
Requirement already satisfied: deprecation in ./sg_env/lib/python3.14/site-packages (from lancedb>=0.5.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 6)) (2.1.0)
Requirement already satisfied: lance-namespace>=0.3.2 in ./sg_env/lib/python3.14/site-packages (from lancedb>=0.5.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 6)) (0.5.2)
Requirement already satisfied: numba>=0.51.2 in ./sg_env/lib/python3.14/site-packages (from umap-learn>=0.5.5->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 8)) (0.64.0)
Requirement already satisfied: pynndescent>=0.5 in ./sg_env/lib/python3.14/site-packages (from umap-learn>=0.5.5->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 8)) (0.6.0)
Requirement already satisfied: setuptools in ./sg_env/lib/python3.14/site-packages (from torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (82.0.1)
Requirement already satisfied: sympy>=1.13.3 in ./sg_env/lib/python3.14/site-packages (from torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (1.14.0)
Requirement already satisfied: networkx>=2.5.1 in ./sg_env/lib/python3.14/site-packages (from torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (3.6.1)
Requirement already satisfied: jinja2 in ./sg_env/lib/python3.14/site-packages (from torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (3.1.6)
Requirement already satisfied: threadpoolctl>=3.2.0 in ./sg_env/lib/python3.14/site-packages (from scikit-learn>=1.4.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 14)) (3.6.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./sg_env/lib/python3.14/site-packages (from pandas>=2.0.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 17)) (2.9.0.post0)
Requirement already satisfied: narwhals>=1.15.1 in ./sg_env/lib/python3.14/site-packages (from plotly>=5.18.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 19)) (2.18.0)
Requirement already satisfied: markdown-it-py>=2.2.0 in ./sg_env/lib/python3.14/site-packages (from rich>=13.0.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 20)) (4.0.0)
Requirement already satisfied: pygments<3.0.0,>=2.13.0 in ./sg_env/lib/python3.14/site-packages (from rich>=13.0.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 20)) (2.19.2)
Requirement already satisfied: lance-namespace-urllib3-client==0.5.2 in ./sg_env/lib/python3.14/site-packages (from lance-namespace>=0.3.2->lancedb>=0.5.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 6)) (0.5.2)
Requirement already satisfied: urllib3<3.0.0,>=1.25.3 in ./sg_env/lib/python3.14/site-packages (from lance-namespace-urllib3-client==0.5.2->lance-namespace>=0.3.2->lancedb>=0.5.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 6)) (2.6.3)
Requirement already satisfied: mdurl~=0.1 in ./sg_env/lib/python3.14/site-packages (from markdown-it-py>=2.2.0->rich>=13.0.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 20)) (0.1.2)
Requirement already satisfied: llvmlite<0.47,>=0.46.0dev0 in ./sg_env/lib/python3.14/site-packages (from numba>=0.51.2->umap-learn>=0.5.5->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 8)) (0.46.0)
Requirement already satisfied: six>=1.5 in ./sg_env/lib/python3.14/site-packages (from python-dateutil>=2.8.2->pandas>=2.0.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 17)) (1.17.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./sg_env/lib/python3.14/site-packages (from sympy>=1.13.3->torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (1.3.0)
Requirement already satisfied: MarkupSafe>=2.0 in ./sg_env/lib/python3.14/site-packages (from jinja2->torch>=2.1.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 11)) (3.0.3)
Requirement already satisfied: shellingham>=1.3.0 in ./sg_env/lib/python3.14/site-packages (from typer->transformers<6.0.0,>=4.41.0->sentence-transformers>=2.3.0->-r /Users/hbauzan/treepwood/semantic_guardtrails/backend/requirements.txt (line 5)) (1.5.4)
Testing /arithmetic...
❌ Error: [Errno 61] Connection refused
\n--- Testing Arithmetic Vector Dimension (/arithmetic) ---
❌ Exception during test: [Errno 61] Connection refused 
Testing /embed...
❌ Error: [Errno 61] Connection refused
\n--- Testing Flight Manifold Boundaries (/galaxy) ---
❌ Exception during flight manifold test [Errno 61] Connection refused
\n--- Testing Tokenize Raw Vector Retention (/tokenize) ---
❌ Exception during tokenize raw vector test [Errno 61] Connection refused
\n--- Testing Vector Distance Integrity (/arithmetic) ---
❌ Exception during vector distance integrity test: [Errno 61] Connection refused 
\n--- Testing Arithmetic Top K Results (/arithmetic) ---
❌ Exception [Errno 61] Connection refused
\n--- Testing Tokenize Raw Vector No NaN 1024D (/tokenize) ---
❌ Exception during Tokenize Raw Vector No NaN 1024D test [Errno 61] Connection refused
\n--- Testing Analyze Dimension Probe (/analyze_dimension) ---
❌ Exception [Errno 61] Connection refused
\n--- Testing Dimension Probe Precision (/analyze_dimension) ---
ℹ️ Probing boundaries [0] and [1023] for magnitude stability...
❌ Exception during probe precision test [Errno 61] Connection refused
\n--- Testing HUD Telemetry Scaling Simulation ---
✅ Max Scale 40960.0 fits neatly inside 100,000 unit Frustum.
\n--- Testing Vector Magnitudes Safe Math Guard ---
✅ SafeMath Vector Magnitudes OK
\n--- Testing XZ Layout 2D Bearing Safe Math Guard ---
✅ SafeMath XZ Layout 2D Bearing OK
\n--- Testing L2 Distance Integrity ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing L2 Frontend-Backend Mathematical Parity ---
❌ Exception in L2 Parity Test: [Errno 61] Connection refused 
\n--- Testing Context Inject Pack Stress (/corpus/inject-pack) ---
❌ Exception during Inject Pack Test: [Errno 61] Connection refused 
\n--- Testing Firewall Trigger Logic (Math Validation) ---
✅ Firewall Logic OK -> Safe: 3.20, Blocked: 48.00 (Threshold: 25.0)
\n--- Testing Single Baseline L2 Audit Tokenization (/tokenize) ---
❌ Exception during Single Baseline L2 Audit test [Errno 61] Connection refused
\n--- Testing L2 Auto-Fit Bounding Box Math ---
✅ Bounding Box Math OK. Projections generated: X=5656.85, Z=5656.85
\n--- Testing Cenital Auto-Fit Camera Math ---
✅ Cenital Auto-Fit Math OK. Deterministic Framing: Y=5775.00, Z=1925.00
\n--- Testing Radar HUD Telemetry Bounds Math Check ---
✅ Radar HUD Telemetry Bounds OK. Deterministic maxRadius calculated as finite number: 3002000.00
\n--- Testing BGE-M3 Vector Parity (Chat Prompt Routing) ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing Async PDF Upload Task Creation (/corpus/upload-pdf) ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing Task Status Endpoint (/corpus/task-status/{task_id}) ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing Firewall Interceptor Blocking Logic ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing Task Status RAM Telemetry (/corpus/task-status/{task_id}) ---
❌ Exception: [Errno 61] Connection refused 
\n--- Testing Streaming Ingestor Generator Pattern ---
✅ Streaming Ingestor Generator Pattern OK
Tests interrupted or completed, cleaning up...
(sg_env) hbauzan ~/treepwood/semantic_guardtrails [real_tests] $ 


*Viewed [run_tests.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_tests.sh) *

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *