#!/bin/bash

# Ensure we're in the repository root
cd "$(dirname "$0")"

echo "=> Activating virtual environment..."
source sg_env/bin/activate

export PYTHONPATH="$(pwd)/backend"
python backend/scripts/commander.py "$@"
