#!/usr/bin/env python3
import sys
import os
import subprocess
import platform
import time
import venv
from pathlib import Path

# --- Configuration ---
MIN_PYTHON_VERSION = (3, 10)

VENV_DIR = Path("lsv_env")
BACKEND_DIR = Path("backend")
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"
DIAGNOSTIC_SCRIPT = BACKEND_DIR / "diagnostic.py"
ENV_FILE = BACKEND_DIR / ".env"

# --- Colors ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(message):
    print(f"\n{Colors.OKCYAN}==> {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.OKGREEN}✔ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✖ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

# --- Helper Functions ---

def check_python_version():
    print_step("Checking Python Version...")
    current_version = sys.version_info
    if current_version < MIN_PYTHON_VERSION:
        print_error(f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ is required. You are running {current_version.major}.{current_version.minor}.")
        sys.exit(1)
    print_success(f"Python {current_version.major}.{current_version.minor} detected.")

def get_venv_python():
    """Returns the path to the python executable within the virtual environment."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"

def ensure_venv():
    print_step("Checking Virtual Environment...")
    if not VENV_DIR.exists():
        print_info(f"Creating virtual environment in {VENV_DIR}...")
        try:
            venv.create(VENV_DIR, with_pip=True)
            print_success("Virtual environment created.")
        except Exception as e:
            print_error(f"Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        print_success("Virtual environment exists.")

    venv_python = get_venv_python()
    if not venv_python.exists():
        print_error(f"Virtual environment python not found at {venv_python}")
        sys.exit(1)
    return str(venv_python)

def install_dependencies(python_path):
    print_step("Installing Dependencies...")
    if not REQUIREMENTS_FILE.exists():
        print_error(f"Requirements file not found at {REQUIREMENTS_FILE}")
        sys.exit(1)

    print_info(f"Installing from {REQUIREMENTS_FILE}...")
    try:
        # Upgrade pip first
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL)
        
        # Install requirements
        # streaming output to user so they see progress
        process = subprocess.Popen(
            [python_path, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        spinner = ['|', '/', '-', '\\']
        idx = 0
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Basic spinner while reading output (or just print last line)
                sys.stdout.write(f"\rInstalling... {spinner[idx % len(spinner)]} {output.strip()[:50].ljust(50)}")
                sys.stdout.flush()
                idx += 1
        
        if process.returncode != 0:
             print_error("Dependency installation failed.")
             print(process.stderr.read())
             sys.exit(1)

        print(f"\rInstalling... Done!                                                 ") # Clear line
        print_success("Dependencies installed.")

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)


def configure_app():
    print_step("Configuration")
    default_model = "BAAI/bge-m3"
    model_name = input(f"{Colors.BOLD}Enter Model Name (Press Enter for default '{default_model}'): {Colors.ENDC}").strip()
    if not model_name:
        model_name = default_model

    hf_token = input(f"{Colors.BOLD}Enter Hugging Face Token (Optional, press Enter to skip): {Colors.ENDC}").strip()
    
    load_demos_input = input(f"{Colors.BOLD}Do you want to load the demo dictionaries (Constitution, Physics, Kitchen)? [Y/n]: {Colors.ENDC}").strip().lower()
    load_demos = "False" if load_demos_input == 'n' else "True"
    
    config_content = f"MODEL_NAME={model_name}\n"
    if hf_token:
        config_content += f"HF_TOKEN={hf_token}\n"
    
    config_content += f"LOAD_DEMOS={load_demos}\n"
    
    # Add recommended robust timeouts
    config_content += "HF_HUB_ETAG_TIMEOUT=30\n"
    config_content += "HF_HUB_DOWNLOAD_TIMEOUT=300\n"
    
    try:
        with open(ENV_FILE, "w") as f:
            f.write(config_content)
        print_success(f"Configuration saved to {ENV_FILE}")
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")

def run_diagnostics(python_path):
    print_step("System Verification")
    if not DIAGNOSTIC_SCRIPT.exists():
        print_error(f"Diagnostic script not found at {DIAGNOSTIC_SCRIPT}")
        return # Not critical enough to exit entire wizard if just diagnostics missing? 
               # User said: "If diagnostics pass, print: "🚀 LSV Engine is Ready!""
               # So it is part of the flow.
        sys.exit(1)

    print_info("Running diagnostics...")
    try:
        # We need to make sure the backend directory is in PYTHONPATH so imports work
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND_DIR.resolve())
        
        subprocess.check_call([python_path, str(DIAGNOSTIC_SCRIPT)], env=env)
        print_success("Diagnostics passed.")
    except subprocess.CalledProcessError:
        print_error("Diagnostics failed. Please check the output above.")
        sys.exit(1)

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Welcome to the LSV Engine (Refactored Strategy) Setup Wizard{Colors.ENDC}")
    print("---------------------------------------")

    check_python_version()
    venv_python = ensure_venv()
    install_dependencies(venv_python)
    configure_app()
    run_diagnostics(venv_python)

    print("\n" + "="*40)
    print(f"{Colors.OKGREEN}{Colors.BOLD}🚀 LSV Engine is Ready!{Colors.ENDC}")
    print(f"To start the server, run:")
    print(f"{Colors.OKCYAN}source lsv_env/bin/activate{Colors.ENDC}  (or {Colors.OKCYAN}lsv_env\\Scripts\\activate{Colors.ENDC} on Windows)")
    print(f"{Colors.OKCYAN}cd backend{Colors.ENDC}")
    print(f"{Colors.OKCYAN}uvicorn app.main:app --reload{Colors.ENDC}")
    print("="*40 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + Colors.WARNING + "Setup cancelled by user." + Colors.ENDC)
        sys.exit(0)
