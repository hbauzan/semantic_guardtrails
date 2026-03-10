#!/bin/bash

# Ensure we're in the repository root
cd "$(dirname "$0")"

echo "=> Activating virtual environment..."
source sg_env/bin/activate

echo "=> Starting Interstitial Cockpit (Frontend)..."
cd frontend
npm run dev
