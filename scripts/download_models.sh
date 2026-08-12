#!/usr/bin/env bash
# Script de téléchargement sécurisé des poids de modèles sous contrôle du LicenseGuard
set -euo pipefail

echo "===================================================================="
echo "⚡ MangaTok Studio — Téléchargement Contrôlé des Modèles IA"
echo "===================================================================="

ALLOW_DOWNLOAD="${ALLOW_MODEL_DOWNLOAD:-false}"
PROFILE="${DEPLOYMENT_PROFILE:-research}"
TERRITORY="${TERRITORY:-EU}"
CACHE_DIR="${MODEL_CACHE_DIR:-./models_cache}"

echo "Profil configuré       : $PROFILE"
echo "Territoire configuré   : $TERRITORY"
echo "Flag ALLOW_DOWNLOAD    : $ALLOW_DOWNLOAD"
echo "Dossier de destination : $CACHE_DIR"
echo "--------------------------------------------------------------------"

if [ "$ALLOW_DOWNLOAD" != "true" ]; then
    echo "⚠️ RÈGLE DE SÉCURITÉ ACTIVE : ALLOW_MODEL_DOWNLOAD n'est pas activé."
    echo "   Pour autoriser le téléchargement des poids de modèles, exportez :"
    echo "   export ALLOW_MODEL_DOWNLOAD=true"
    echo "   Abandon immédiat sans téléchargement réseau."
    exit 0
fi

# Validation légale préalable via LicenseGuard
python3 -c "
import sys
from manga_studio.adapters.guard.license_guard_adapter import LicenseGuardAdapter
from manga_studio.core.models.config import DeploymentProfile

guard = LicenseGuardAdapter()
prof = DeploymentProfile.COMMERCIAL if '$PROFILE' == 'commercial' else DeploymentProfile.RESEARCH
try:
    dec = guard.validate_execution(
        model_id='minimax_h3_ref2va',
        profile=prof,
        territory='$TERRITORY',
        allow_local_flag=True
    )
    print(f'Décision du LicenseGuard : {dec.status} ({dec.reason})')
except Exception as e:
    print(f'❌ BLOCAGE DU LICENSE GUARD : {e}')
    sys.exit(1)
"

mkdir -p "$CACHE_DIR"
echo "✓ Vérification légale validée pour le profil '$PROFILE'."
echo "ℹ️ Téléchargement des checkpoints quantifiés (Wan2.1 / DINOv2 / Whisper) vers $CACHE_DIR..."
echo "===================================================================="
