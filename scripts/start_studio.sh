#!/usr/bin/env bash
# Script de lancement tout-en-un du Studio MangaTok (Vérifications + FastAPI)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "===================================================================="
echo "⚡ Démarrage de MangaTok Studio — Mode « Conte animé »"
echo "===================================================================="

# 1. Vérification de l'environnement
"$SCRIPT_DIR/setup_dev.sh"

# 2. Validation rapide des schémas
"$SCRIPT_DIR/validate_schemas.sh"

# 3. Lancement du serveur Web et API
echo "--------------------------------------------------------------------"
echo "🚀 Lancement du serveur API FastAPI sur http://0.0.0.0:8000..."
echo "   Appuyez sur Ctrl+C pour arrêter le studio."
echo "--------------------------------------------------------------------"

cd "$ROOT_DIR"
exec uvicorn manga_studio.api.app:app --host 0.0.0.0 --port 8000
