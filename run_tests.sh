#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🧹 Clearing Vite and Build caches..."
rm -rf "$PROJECT_ROOT/frontend/node_modules/.vite"
rm -rf "$PROJECT_ROOT/frontend/node_modules/.cache"
rm -rf "$PROJECT_ROOT/frontend/dist"

echo "👁️ Deep Observability Testing Initialized."
echo "🤖 Checking Sovereign Ollama Motor..."
"$PROJECT_ROOT/sovereign.sh" check || echo "⚠️ Proceeding without Ollama. RAG tests may fail."

source "$PROJECT_ROOT/sg_env/bin/activate"
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
python3 backend/perform_tests.py
