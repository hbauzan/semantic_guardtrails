import os
import json
import sys
from datetime import datetime

"""
===============================================================================
HOW-TO-USE: LSV ORCHESTRATOR (SSA PROTOCOL) - SEMANTIC GUARDTRAILS
===============================================================================
1. PRE-REQUISITO: Estar en la raíz del proyecto.
2. ACTIVACIÓN: 
   $ source sg_env/bin/activate
3. CONFIGURACIÓN:
   - 'mision': Perfil base de archivos.
   - 'extras': Archivos específicos para la tarea actual.
4. EJECUCIÓN:
   $ python3 lsv_packager.py
5. FLUJO:
   - Verifica venv activo.
   - Genera 'sg_context.txt' unificando Specs, Manifiesto y Código.
===============================================================================
"""

class LSVOrchestrator:
    def __init__(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.manifest_path = os.path.join(self.root, "manifest.json")
        self.vital_files = [
            "architecture_spec.md", 
            "manifest.json", 
            "backend/perform_tests.py",
            "run_server.sh",          
            "run_tests.sh",
            "run_ui.sh",
            "run_commander.sh",
            "bootstrap.sh"
        ]
        
    def check_venv(self):
        """Bloquea la ejecución si el venv no está activo."""
        if not hasattr(sys, 'real_prefix') and not (sys.base_prefix != sys.prefix):
            print("❌ ERROR: El entorno virtual (sg_env) NO está activo.")
            print("Ejecutá: source sg_env/bin/activate")
            sys.exit(1)

    def get_profile(self, profile_name):
        profiles = {
            "arithmetic": [
                "frontend/src/ArithmeticVisualizer.tsx",
                "backend/app/api/routes.py",
                "backend/app/core/dependencies.py"
            ]
        }
        return profiles.get(profile_name, [])

    def validate_state(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                m = json.load(f)
                print(f"\n🛰️  SYSTEM STATE v{m.get('version')}")
                for feat in m.get("active_features", []):
                    print(f"[✅ LIVE] {feat}")
                print("-" * 35)

    def create_bundle(self, files, output_name="sg_context.txt"):
        final_list = list(dict.fromkeys(self.vital_files + files))
        with open(output_name, "w", encoding="utf-8") as out:
            out.write(f"SEMANTIC GUARDTRAILS BUNDLE // GENERATED: {datetime.now()}\n\n")
            for file_path in final_list:
                if os.path.exists(file_path):
                    out.write(f"\n{'#'*80}\nFILE: {file_path}\n{'#'*80}\n\n")
                    with open(file_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                else:
                    print(f"⚠️ Warning: {file_path} no encontrado.")

if __name__ == "__main__":
    orchestrator = LSVOrchestrator()
    orchestrator.check_venv()
    orchestrator.validate_state()
    
    mision = orchestrator.get_profile("arithmetic")
    
    extras = [
        "README.md",
        "backend/requirements.txt",
        "frontend/package.json",
        "backend/app/modules/storage.py",
        "backend/app/core/config.py",
        "backend/app/modules/context_vault.py",
        "backend/app/main.py",
        "backend/recalibrate.py",
        "backend/app/modules/embedder.py",
        "backend/scripts/commander.py",
        "frontend/src/store.ts",
        "frontend/src/App.tsx",
        "lsv_packager.py"
    ]
    
    orchestrator.create_bundle(mision + extras)
    print(f"🚀 [SSA] Contexto total generado: {os.path.abspath('sg_context.txt')}")
