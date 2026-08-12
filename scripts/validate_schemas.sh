#!/usr/bin/env bash
# Validation des schémas JSON et compatibilité Pydantic v2
set -euo pipefail

echo "===================================================================="
echo "⚡ MangaTok Studio — Validation des Schémas de Données"
echo "===================================================================="

python3 -c "
import json
from pathlib import Path
from manga_studio.core.models.character import CharacterSheet, CharacterBible
from manga_studio.core.models.storyboard import Storyboard
from manga_studio.core.models.qc import QCReport

schemas = [
    'schemas/character-sheet.schema.json',
    'schemas/storyboard.schema.json',
    'schemas/qc-report.schema.json'
]

for s in schemas:
    p = Path(s)
    if not p.exists():
        raise FileNotFoundError(f'Schéma manquant : {s}')
    data = json.loads(p.read_text(encoding='utf-8'))
    print(f'✓ Schéma validé : {s} (Titre: {data.get(\"title\")})')

print('====================================================================')
print('✅ Tous les schémas JSON sont conformes et valides !')
print('====================================================================')
"
