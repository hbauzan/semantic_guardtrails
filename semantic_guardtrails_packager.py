import os
import json
import sys
from datetime import datetime

"""
===============================================================================
HOW-TO-USE: SEMANTIC GUARDRAILS ORCHESTRATOR (SSA PROTOCOL)
===============================================================================
1. PRE-REQUISITO: Estar en la raíz del proyecto.
2. ACTIVACIÓN: 
   $ source sg_env/bin/activate
3. CONFIGURACIÓN:
   - 'mision': Perfil base de archivos ('api' o 'engine').
   - 'extras': Archivos específicos para la tarea actual.
4. EJECUCIÓN:
   $ ./run_pack.sh
5. FLUJO:
   - Verifica venv activo.
   - Genera 'semantic_guardtrails_context.txt' unificando Specs, Manifiesto y Código.
===============================================================================
"""

class SemanticGuardtrailsOrchestrator:
    def __init__(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.manifest_path = os.path.join(self.root, "manifest.json")
        self.vital_files =[
            "architecture_spec.md", 
            "manifest.json", 
            "run_pack.sh"
        ]
        
    def check_venv(self):
        """Bloquea la ejecución si el venv no está activo."""
        if not hasattr(sys, 'real_prefix') and not (sys.base_prefix != sys.prefix):
            print("❌ ERROR: El entorno virtual (sg_env) NO está activo.")
            print("Ejecutá: source sg_env/bin/activate")
            sys.exit(1)

    def get_profile(self, profile_name):
        """Perfiles actualizados para la arquitectura FastAPI + LanceDB."""
        profiles = {
            "api":[
                "backend/app/main.py",
                "backend/app/api/routes.py"
            ],
            "engine":[
                "backend/app/modules/storage.py",
                "backend/app/modules/embedder.py",
                "backend/app/modules/geometry.py"
            ]
        }
        return profiles.get(profile_name,[])

    def validate_state(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                m = json.load(f)
                print(f"\n🛰️  SYSTEM STATE v{m.get('version', 'UNKNOWN')}")
                for feat, active in m.get("active_features", {}).items():
                    print(f"[{'✅ LIVE' if active else '⏳ PENDING'}] {feat}")
                print("-" * 35)
        else:
            print("⚠️ Warning: manifest.json no encontrado.")

    def create_bundle(self, files, output_name="semantic_guardtrails_context.txt"):
        final_list = list(dict.fromkeys(self.vital_files + files))
        with open(output_name, "w", encoding="utf-8") as out:
            out.write(f"SEMANTIC GUARDRAILS CONTEXT BUNDLE // GENERATED: {datetime.now()}\n\n")
            for file_path in final_list:
                full_path = os.path.join(self.root, file_path)
                if os.path.exists(full_path):
                    out.write(f"\n{'#'*80}\nFILE: {file_path}\n{'#'*80}\n\n")
                    with open(full_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                else:
                    print(f"⚠️ Warning: {file_path} no encontrado. Omitiendo...")

if __name__ == "__main__":
    orchestrator = SemanticGuardtrailsOrchestrator()
    orchestrator.check_venv()
    orchestrator.validate_state()
    
    # --- CONFIGURACIÓN FASE ACTUAL ---
    # Cambiar a "engine" si se trabaja en el motor vectorial
    mision = orchestrator.get_profile("api")
    
    # Archivos extra adaptados al nuevo proyecto
    extras =[
        "backend/requirements.txt",
        "backend/.env"
    ]
    
    orchestrator.create_bundle(mision + extras)
    print(f"🚀 [SSA] Contexto total generado: {os.path.abspath('semantic_guardtrails_context.txt')}")