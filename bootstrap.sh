#!/bin/bash
set -e
echo "🛠️ Bootstrapping Semantic Guardrails..."
python3 -m venv sg_env
source sg_env/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
mkdir -p backend/data/lancedb
echo "✅ Entorno sg_env creado y dependencias instaladas."
