#!/bin/bash
# sovereign.sh - Manage Ollama daemon for Local RAG & Semantic Firewall

set -e

ACTION=$1

case $ACTION in
  "check")
    echo "🔍 Checking Ollama Motor Status..."
    if curl -s http://localhost:11434 > /dev/null; then
        echo "✅ Ollama is RUNNING."
    else
        echo "❌ Ollama is OFFLINE or NOT INSTALLED."
    fi
    ;;
  "serve")
    echo "🚀 Starting Ollama with OLLAMA_HOST=0.0.0.0..."
    OLLAMA_HOST=0.0.0.0 ollama serve
    ;;
  "pull")
    MODEL=${2:-llama3.1}
    echo "📥 Pulling local model: $MODEL"
    ollama pull $MODEL
    ;;
  *)
    echo "Usage: ./sovereign.sh [check|serve|pull <model>]"
    ;;
esac
