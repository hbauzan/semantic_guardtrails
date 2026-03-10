#!/bin/bash
set -e
PORT=8000
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "🚀 Iniciando Semantic Guardrails Backend"
source "$PROJECT_ROOT/sg_env/bin/activate"
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT/backend"
cd "$PROJECT_ROOT/backend"
uvicorn app.main:app --reload --host 127.0.0.1 --port $PORT
