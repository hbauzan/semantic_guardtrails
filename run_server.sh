#!/bin/bash
set -e
PORT=8000
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🧹 Clearing Vite and Build caches..."
rm -rf "$PROJECT_ROOT/frontend/node_modules/.vite"
rm -rf "$PROJECT_ROOT/frontend/node_modules/.cache"
rm -rf "$PROJECT_ROOT/frontend/dist"

# 1. Limpieza de Puertos
PID=$(lsof -ti :$PORT || true)
if [ ! -z "$PID" ]; then
    echo "⚠️  Puerto $PORT ocupado (PID: $PID). Ejecutando limpieza..."
    kill -9 $PID || true
    sleep 1
fi
echo "👁️ Deep Observability Active. Infinite View & Crosshair Online."
echo "🤖 Checking Sovereign Ollama Motor..."
"$PROJECT_ROOT/sovereign.sh" check || echo "⚠️ Proceeding without Ollama. RAG may fail."

echo "🚀 Iniciando Semantic Guardrails Backend"
source "$PROJECT_ROOT/sg_env/bin/activate"
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT/backend"
cd "$PROJECT_ROOT/backend"
uvicorn app.main:app --reload --host 127.0.0.1 --port $PORT
