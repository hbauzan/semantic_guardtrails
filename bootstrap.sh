#!/bin/bash
set -e

echo "=> Bootstrapping Semantic Guardtrails..."

if [ ! -d "sg_env" ]; then
    echo "=> Creating virtual environment sg_env..."
    python3 -m venv sg_env
fi

echo "=> Activating sg_env..."
source sg_env/bin/activate

echo "=> Installing backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo "=> Warning: backend/requirements.txt not found. Skipping pip install."
fi

echo "=> Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    cd ..
fi

echo "=> Creating data directories..."
mkdir -p data/lancedb
mkdir -p data/sqlite

echo "=> Triggering recalibration..."
export PYTHONPATH="$(pwd)/backend"
if [ -f "backend/recalibrate.py" ]; then
    python backend/recalibrate.py
else
    echo "=> Warning: backend/recalibrate.py not found. Skipping."
fi

echo "=> Bootstrap complete!"
