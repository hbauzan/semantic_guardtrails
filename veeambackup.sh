#!/bin/bash
set -e
DATE=$(date +%Y%m%d_%H%M%S)
echo "📦 Generando backup de Semantic Guardrails..."
tar -czvf "sg_backup_$DATE.tar.gz" . --exclude="sg_env" --exclude="frontend/node_modules" --exclude="backend/data" --exclude=".git"
echo "✅ Backup sg_backup_$DATE.tar.gz completado."
