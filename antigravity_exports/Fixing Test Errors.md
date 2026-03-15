# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

# TASK: FIX NAMERROR AND OPTIMIZE ASYNC PDF INGESTION (routes.py)
CONTEXT:
We recently refactored process_pdf_background in backend/app/api/routes.py to run via asyncio.to_thread to prevent blocking the FastAPI event loop during PyMuPDF (fitz) execution and ML inference.
CURRENT ISSUES:
Execution Crash: The background thread throws NameError: name 'fitz' is not defined, NameError: name 'gc' is not defined, and NameError: name 'psutil' is not defined. The local imports inside the function were removed, but the global imports at the top of the file are missing.
Performance Bottleneck: The user reported that "PDF injection is extremely slow." While ML inference is inherently heavy, blocking the main event loop makes the entire application freeze, exacerbating the perceived slowness. We must ensure the CPU-bound tasks (PyMuPDF extraction and BGE-M3 encoding) are fully offloaded to the worker thread and do not choke the API.
DIRECTIVES:
Fix Imports (backend/app/api/routes.py):
Ensure the following libraries are imported globally at the very top of the file: import fitz, import gc, import psutil, import time, import asyncio.
Verify that process_pdf_background is correctly structured to access these global imports when invoked via asyncio.to_thread.
Performance & Threading Audit:
Verify that asyncio.to_thread(process_pdf_background, ...) is correctly implemented in the /corpus/upload-pdf endpoint.
Ensure that the FastAPI worker is immediately returning the task_id while the heavy extraction and vectorization happen entirely in the background thread.
Documentation Loop (MANDATORY):
Every functional change MUST be accompanied by:
An update to manifest.json (ensure features like "async_pdf_vectorization": true and add/set "non_blocking_ingestion": true).
An update to architecture_spec.md reflecting the new asyncio.to_thread non-blocking logic for PDF ingestion.
Testing Sovereignty (MANDATORY):
backend/perform_tests.py is the System Heartbeat.
If a logic change requires a new validation, you must suggest and add the specific test function.
Action: Add a test named test_pdf_ingestion_non_blocking_and_imports to perform_tests.py. This test must upload a dummy PDF, assert that the endpoint returns a 200 OK immediately (proving it's non-blocking), and then poll the /corpus/task-status/{task_id} endpoint briefly to ensure the status transitions to processing or completed without throwing a 500 Internal Server Error or NameError.
Execution & Verification:
Update run_server.sh and run_tests.sh if any environment or execution flags need adjustment.
Execute ./run_tests.sh and ensure all tests (including your new one) pass.
Execute ./run_server.sh to ensure the application boots successfully without import errors.

*Searched filesystem*

*Searched filesystem*

*Searched filesystem*

*Searched filesystem*

*Edited relevant file*

*Viewed [routes.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/api/routes.py) *

*Viewed [manifest.json](file:///Users/hbauzan/treepwood/semantic_guardtrails/manifest.json) *

*Viewed [architecture_spec.md](file:///Users/hbauzan/treepwood/semantic_guardtrails/architecture_spec.md) *

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Edited relevant file*

*User accepted the command `./run_server.sh`*

*User accepted the command `./run_tests.sh`*

*Edited relevant file*

*Checked command status*

*User accepted the command `curl http://127.0.0.1:8000/system/stats`*

*Checked command status*

*Viewed [run_server.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_server.sh) *

*Viewed [run_tests.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_tests.sh) *

*User accepted the command `source ../sg_env/bin/activate && export PYTHONPATH=$PYTHONPATH:$(pwd) && uvicorn app.main:app --host 127.0.0.1 --port 8000`*

*Checked command status*

*User accepted the command `./run_tests.sh`*

*Checked command status*

*Checked command status*

*Checked command status*

*User accepted the command `python3 -c "import sys; sys.path.append('backend'); import perform_tests; perform_tests.test_pdf_ingestion_non_blocking_and_imports()"`*

*Checked command status*

*Viewed [ingestor.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/modules/ingestor.py) *

*Edited relevant file*

*User accepted the command `./run_tests.sh`*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*User accepted the command `lsof -ti:8000 | xargs kill -9 || true`*

*User accepted the command `./run_server.sh`*

*User accepted the command `./run_tests.sh`*

*Checked command status*

*Checked command status*

*Checked command status*

*User accepted the command `lsof -ti:8000 | xargs kill -9 || true`*

*User accepted the command `./run_server.sh`*

*User accepted the command `./run_tests.sh`*

*Checked command status*

*Checked command status*

*Checked command status*

*Edited relevant file*

### User Input

me dio un error:

NFO:     127.0.0.1:57641 - "GET /corpus/task-status/e3f155ca-6b25-472a-9bc7-b840518e233d HTTP/1.1" 200 OK
⚡ [TASK e3f155ca-6b25-472a-9bc7-b840518e233d] Batch procesado (384/635)
INFO:     127.0.0.1:57763 - "GET /system/stats HTTP/1.1" 200 OK
⚡ [TASK e3f155ca-6b25-472a-9bc7-b840518e233d] Batch procesado (512/635)
❌ [TASK e3f155ca-6b25-472a-9bc7-b840518e233d] ERROR FATAL: MPS backend out of memory (MPS allocated: 7.80 GiB, other allocations: 6.94 GiB, max allowed: 18.13 GiB). Tried to allocate 3.46 GiB on private pool. Use PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 to disable upper limit for memory allocations (may cause system failure).
INFO:     127.0.0.1:58090 - "GET /corpus/task-status/e3f155ca-6b25-472a-9bc7-b840518e233d HTTP/1.1" 200 OK
INFO:     127.0.0.1:58090 - "GET /system/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:58090 - "GET /system/stats HTTP/1.1" 200 OK


*Viewed [routes.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/api/routes.py) *

*Viewed [embedder.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/app/modules/embedder.py) *

*Edited relevant file*

*Edited relevant file*

*User accepted the command `lsof -ti:8000 | xargs kill -9 || true`*

*User accepted the command `./run_server.sh`*

*User accepted the command `./run_tests.sh`*

*Checked command status*

### User Input

please address the two errors in tests:

(sg_env) hbauzan ~/treepwood/semantic_guardtrails [real_tests] $ ./run_tests.sh
🧹 Clearing Vite and Build caches...
👁️ Deep Observability Testing Initialized.
🤖 Checking Sovereign Ollama Motor...
🔍 Checking Ollama Motor Status...
❌ Ollama is OFFLINE or NOT INSTALLED.
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
✅ Arithmetic OK
\n--- Testing Arithmetic Vector Dimension (/arithmetic) ---
❌ Results length does not match top_k=3. Got: 2 
Testing /embed...
✅ Embed OK
\n--- Testing Flight Manifold Boundaries (/galaxy) ---
✅ Flight Manifold Check: All coordinates within [0, 300] safe flight zone.
\n--- Testing Tokenize Raw Vector Retention (/tokenize) ---
✅ Tokenize Raw Vector Retention OK
\n--- Testing Vector Distance Integrity (/arithmetic) ---
✅ Vector Distance Integrity OK - 1024D vector reliably provided.
\n--- Testing Arithmetic Top K Results (/arithmetic) ---
✅ Arithmetic Top K Results OK
\n--- Testing Tokenize Raw Vector No NaN 1024D (/tokenize) ---
✅ Tokenize Raw Vector No NaN 1024D OK
\n--- Testing Analyze Dimension Probe (/analyze_dimension) ---
✅ Analyze Dimension Probe OK
\n--- Testing Dimension Probe Precision (/analyze_dimension) ---
ℹ️ Probing boundaries [0] and [1023] for magnitude stability...
✅ Dimension Probe Precision bounds OK
\n--- Testing HUD Telemetry Scaling Simulation ---
✅ Max Scale 40960.0 fits neatly inside 100,000 unit Frustum.
\n--- Testing Vector Magnitudes Safe Math Guard ---
✅ SafeMath Vector Magnitudes OK
\n--- Testing XZ Layout 2D Bearing Safe Math Guard ---
✅ SafeMath XZ Layout 2D Bearing OK
\n--- Testing L2 Distance Integrity ---
✅ L2 Distance Integrity OK. Endpoint is stable with new metric.
\n--- Testing L2 Frontend-Backend Mathematical Parity ---
✅ L2 Parity Verified: Frontend (2.1660) == Backend (2.1660)
\n--- Testing Context Inject Pack Stress (/corpus/inject-pack) ---
✅ Context Inject Pack OK
\n--- Testing Firewall Trigger Logic (Math Validation) ---
✅ Firewall Logic OK -> Safe: 3.20, Blocked: 48.00 (Threshold: 25.0)
\n--- Testing Single Baseline L2 Audit Tokenization (/tokenize) ---
✅ Single Baseline L2 Audit Tokenization OK. (Dn: 21.4788)
\n--- Testing L2 Auto-Fit Bounding Box Math ---
✅ Bounding Box Math OK. Projections generated: X=5656.85, Z=5656.85
\n--- Testing Cenital Auto-Fit Camera Math ---
✅ Cenital Auto-Fit Math OK. Deterministic Framing: Y=5775.00, Z=1925.00
\n--- Testing Radar HUD Telemetry Bounds Math Check ---
✅ Radar HUD Telemetry Bounds OK. Deterministic maxRadius calculated as finite number: 3002000.00
\n--- Testing BGE-M3 Vector Parity (Chat Prompt Routing) ---
✅ Chat prompt Vector Parity OK
\n--- Testing Async PDF Upload Task Creation (/corpus/upload-pdf) ---
✅ Async PDF Upload Task Creation OK (Task ID: bec4bf43-a5a4-4559-b18c-d4ce14115d3e)
\n--- Testing Task Status Endpoint (/corpus/task-status/{task_id}) ---
✅ Task Status Endpoint OK (Status: error)
\n--- Testing Firewall Interceptor Blocking Logic ---
✅ Firewall Interceptor Blocking Logic OK
\n--- Testing Task Status RAM Telemetry (/corpus/task-status/{task_id}) ---
✅ Task Status RAM Telemetry OK (RAM: 0 MB)
\n--- Testing Streaming Ingestor Generator Pattern ---
✅ Streaming Ingestor Generator Pattern OK
\n--- Testing System Stats Telemetry (/system/stats) ---
✅ System Stats Endpoint OK
\n--- Testing ETR Telemetry Math Logic (/corpus/task-status/{task_id}) ---
✅ ETR Telemetry Math OK. (Simulated ETR: 0ms)
\n--- Testing PDF Ingestion Non-Blocking and Imports (/corpus/upload-pdf) ---
✅ PDF Ingestion Non-Blocking and Imports OK (Completed without errors)
Tests interrupted or completed, cleaning up...
(sg_env) hbauzan ~/treepwood/semantic_guardtrails [real_tests] $ 


*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Edited relevant file*

*User accepted the command `./run_tests.sh`*

*Edited relevant file*