#!/usr/bin/env bash
# Nettoyage des caches et fichiers temporaires
set -euo pipefail

echo "==> Suppression des fichiers temporaires, caches pytest et builds..."

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
rm -rf .coverage htmlcov/ dist/ build/ *.egg-info output/ ci_demo_output/ 2>/dev/null || true

echo "✓ Nettoyage terminé."
