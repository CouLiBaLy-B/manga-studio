#!/usr/bin/env bash
# Exécute une démonstration complète du pipeline Conte animé sur le conte de Râ
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

OUTPUT_DIR="$ROOT_DIR/demo_output"
STORY_PATH="$ROOT_DIR/tests/fixtures/conte.txt"
CHARS_DIR="$ROOT_DIR/tests/fixtures/personnages"

echo "===================================================================="
echo "⚡ MangaTok Studio — Lancement de la démo « Conte animé »"
echo "===================================================================="
echo "Conte source    : $STORY_PATH"
echo "Personnages     : $CHARS_DIR"
echo "Dossier sortie  : $OUTPUT_DIR"
echo "--------------------------------------------------------------------"

python3 -m manga_studio.cli.main \
    --story "$STORY_PATH" \
    --characters-dir "$CHARS_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --profile "research" \
    --territory "EU" \
    --use-mock-video

echo "--------------------------------------------------------------------"
echo "✅ Démonstration terminée avec succès !"
echo "Artefacts générés dans : $OUTPUT_DIR"
echo "- Vidéo finale     : $OUTPUT_DIR/conte_final.mp4"
echo "- Bible personnage : $OUTPUT_DIR/character_bible.json"
echo "- Storyboard validé: $OUTPUT_DIR/storyboard.validated.json"
echo "- Sous-titres      : $OUTPUT_DIR/subtitles/conte.srt"
echo "- Manifest d'audit : $OUTPUT_DIR/manifests/run_report.json"
echo "===================================================================="
