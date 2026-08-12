#!/usr/bin/env bash
# Script d'initialisation de l'environnement de développement MangaTok Studio
set -euo pipefail

echo "===================================================================="
echo "⚡ Configuration de l'environnement MangaTok Studio"
echo "===================================================================="

# 1. Vérification de Python
PYTHON_BIN=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Erreur : Python 3.10+ est requis mais introuvable."
    exit 1
fi
echo "✓ Python détecté : $("$PYTHON_BIN" --version)"

# 2. Vérification des outils multimédia (FFmpeg / FFprobe)
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✓ FFmpeg disponible : $(ffmpeg -version | head -n 1)"
else
    echo "⚠️ Avertissement : FFmpeg n'est pas installé dans le PATH système."
    echo "   Le pipeline utilisera le multiplexage autonome de secours."
fi

# 3. Vérification de l'accélération GPU (NVIDIA CUDA)
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "✓ GPU NVIDIA détecté :"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
else
    echo "ℹ️ Information : Aucun GPU NVIDIA détecté via nvidia-smi. Mode CPU / Mocks actif."
fi

# 4. Installation du package en mode éditable
echo "==> Installation du package local manga-studio..."
"$PYTHON_BIN" -m pip install -e .
"$PYTHON_BIN" -m pip install pytest pytest-cov httpx fastapi uvicorn pillow jinja2 pydantic

echo "===================================================================="
echo "✅ Environnement prêt ! Lancez 'make test' ou 'make run-demo'."
echo "===================================================================="
