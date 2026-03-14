#!/bin/bash

# SSA V19: Commander TUI
# Senior IT Architect / Systems Specialist
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

function show_main_menu() {
    clear
    echo "========================================="
    echo "    SEMANTIC GUARDTRAILS COMMANDER       "
    echo "========================================="
    echo "  [S] START ENGINE (run_server.sh)"
    echo "  [T] RUN TESTS (run_tests.sh)"
    echo "  [O] OLLAMA MOTOR"
    echo "  [X] EXIT"
    echo "========================================="
    read -p "Select an option: " choice
    case "$choice" in
        [Ss]* ) 
            "$PROJECT_ROOT/run_server.sh"
            echo "Press Enter to return..."
            read
            show_main_menu
            ;;
        [Tt]* ) 
            "$PROJECT_ROOT/run_tests.sh"
            echo "Press Enter to return..."
            read
            show_main_menu
            ;;
        [Oo]* ) show_ollama_menu;;
        [Xx]* ) exit 0;;
        * ) echo "Invalid option."; sleep 1; show_main_menu;;
    esac
}

function show_ollama_menu() {
    clear
    echo "========================================="
    echo "            OLLAMA MOTOR                 "
    echo "========================================="
    echo "  [A] Check Status"
    echo "  [B] Start Motor (Auto-Clear Port)"
    echo "  [C] Pull Model"
    echo "  [D] List Models"
    echo "  [R] RETURN TO MAIN MENU"
    echo "========================================="
    read -p "Select an option: " choice
    case "$choice" in
        [Aa]* ) 
            echo "Checking status..."
            ps aux | grep "[o]llama" || echo "Ollama is not running."
            read -p "Press Enter to continue..."
            show_ollama_menu
            ;;
        [Bb]* ) 
            echo "Clearing port 11434..."
            lsof -ti:11434 | xargs kill -9 2>/dev/null || true
            echo "Starting Ollama Motor..."
            export OLLAMA_HOST=0.0.0.0
            "$PROJECT_ROOT/sovereign.sh" serve
            read -p "Press Enter to continue..."
            show_ollama_menu
            ;;
        [Cc]* ) 
            read -p "Enter model name [default: llama3.1]: " model
            model=${model:-llama3.1}
            ollama pull "$model"
            read -p "Press Enter to continue..."
            show_ollama_menu
            ;;
        [Dd]* ) 
            ollama list
            read -p "Press Enter to continue..."
            show_ollama_menu
            ;;
        [Rr]* ) show_main_menu;;
        * ) echo "Invalid option."; sleep 1; show_ollama_menu;;
    esac
}

show_main_menu
