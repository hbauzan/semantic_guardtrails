#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/sg_env/bin/activate"
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
python3 backend/scripts/commander.py
