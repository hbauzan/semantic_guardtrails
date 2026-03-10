# Architecture Specification: Semantic Guardrails

## 1. Stack
* **API Server:** FastAPI (Uvicorn)
* **Vector Engine:** LanceDB (BGE-M3 1024D)
* **Environment:** `sg_env`

## 2. Core Endpoints
* `POST /embed`: Text to 1024D vector.
* `POST /arithmetic`: Vector math (`A - B + C`).

## 3. Tooling
* **Context Packager:** `semantic_guardtrails_packager.py` (Triggered via `run_pack.sh`). Generates unified context bundles for LLM ingestion, enforcing `sg_env` validation and state checks.

## 6. Current Flight Status
### Navigation & Flight Mechanics
*   **Smooth Flight**: Inertia-based camera movement with drag damping (AWSD + QE).
*   **Hyper-Boost**: Exponential thrust accumulation (Shift key) with drag bleed-off.
*   **Mouse Look**: `PointerLockControls` integrated with global click-to-lock, featuring 2e-compliant input suppression (ignores typing in text fields).