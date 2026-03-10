#!/bin/bash

# Ensure we're in the repository root
cd "$(dirname "$0")"

echo "=> Activating virtual environment..."
source sg_env/bin/activate

echo "=> Starting LSV Engine (Backend)..."
export PYTHONPATH="$(pwd)/backend"
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
