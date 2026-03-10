# Architecture Specification (Semantic Guardtrails)

This document outlines the architecture for the Semantic Guardtrails system, an adaptation of the original "Crystal Box" project focused on vector arithmetic and semantic safety.

## 1. System Stack

**Backend System Overview**
- **Framework:** FastAPI
- **Port:** HTTP 8000
- **Primary Language:** Python 3 (Virtual Environment: `sg_env`)
- **Embedding Model:** BGE-M3 (strict 1024D vectors)
- **Vector Database:** LanceDB (CrystalVault)
- **Relational Database:** SQLite (ContextVault)

**Frontend System Overview**
- **Framework:** React / Vite
- **Port:** HTTP 5173
- **Primary Language:** TypeScript
- **Styling:** CSS Modular / Vanilla

## 2. Directory Map

```text
/semantic_guardtrails
├── backend/
│   ├── main.py (FastAPI application entrypoint)
│   ├── api/ (Endpoints implementation)
│   ├── core/ (Models, embeddings mapping, engine logic)
│   ├── db/ (LanceDB and SQLite connectors)
│   ├── scripts/ (Automation scripts like commander.py, recalibrate.py)
│   └── tests/ (perform_tests.py, test suite)
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/ (HUD, Visualizers)
│   │   └── store/ (Frontend state logic)
├── data/
│   ├── lancedb/ (CrystalVault vector data)
│   └── sqlite/ (ContextVault relational data)
├── sg_env/ (Isolated virtual environment)
├── architecture_spec.md (This file)
├── manifest.json
└── *.sh (Root orchestration scripts)
```

## 3. API Contracts

The backend exposes the following primary endpoints to interface with the 1024D latent space:

### `POST /embed`
Generates a 1024D embedding representation of the inputted text.
- **Request Body:**
  ```json
  { "text": "String to be embedded" }
  ```
- **Response:**
  ```json
  { "vector": [0.123, -0.456, ... (1024 floats)], "dimensions": 1024 }
  ```

### `POST /tokenize`
Breaks physical text into underlying neuro-linguistic tokens prior to embedding processing.
- **Request Body:**
  ```json
  { "text": "String to be tokenized" }
  ```
- **Response:**
  ```json
  { "tokens": ["String", "to", "be", "tokenized"] }
  ```

### `POST /arithmetic`
Performs vector arithmetic operations (addition, subtraction, scaling) within the latent space and returns the output vector alongside context distances against guardrails.
- **Request Body:**
  ```json
  {
    "operation": "add",
    "vectors": [[...], [...]]
  }
  ```
- **Response:**
  ```json
  {
    "result_vector": [...],
    "closest_matches": [...]
  }
  ```
