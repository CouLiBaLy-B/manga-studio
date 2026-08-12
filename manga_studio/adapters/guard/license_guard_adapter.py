"""Adaptateur de vérification et de gouvernance des licences de modèles."""

import logging
from typing import Optional
from manga_studio.core.models.config import DeploymentProfile
from manga_studio.core.ports.license_guard import (
    GuardDecision,
    LicenseGuardPort,
    LicenseViolationError,
)
from manga_studio.core.ports.model_registry import ModelRegistryPort

logger = logging.getLogger(__name__)


class LicenseGuardAdapter(LicenseGuardPort):
    """Garde-fou assurant la conformité juridique, territoriale et commerciale des modèles."""

    EXCLUDED_H3_TERRITORIES = {"EU", "US", "UK", "KR", "FR", "DE", "IT", "ES"}

    def __init__(self, model_registry: Optional[ModelRegistryPort] = None):
        self.model_registry = model_registry

    def validate_execution(
        self,
        model_id: str,
        profile: DeploymentProfile,
        territory: str,
        allow_local_flag: bool = False
    ) -> GuardDecision:
        """Vérifie la conformité de l'utilisation d'un modèle selon le contexte."""
        territory_upper = territory.upper()

        # Règle MiniMax H3
        if "h3" in model_id.lower() or "minimax" in model_id.lower():
            license_name = "MiniMax H3 Community License Agreement (2026-08-02)"
            
            # Blocage commercial strict en territoire exclu
            if profile == DeploymentProfile.COMMERCIAL and territory_upper in self.EXCLUDED_H3_TERRITORIES:
                reason = (
                    f"VIOLATION DE LICENCE : L'exécution locale de MiniMax H3 et le déploiement de ses outputs "
                    f"sont expressément interdits dans le territoire '{territory_upper}' sous la licence H3 Community. "
                    f"Utilisation commerciale refusée."
                )
                logger.error(f"[LicenseGuard] {reason}")
                raise LicenseViolationError(reason)

            # Règle d'activation locale explicite
            if not allow_local_flag:
                reason = (
                    "Le modèle MiniMax H3 nécessite une activation explicite via ENABLE_H3_LOCAL=true."
                )
                return GuardDecision(
                    approved=False,
                    status="BLOCKED",
                    reason=reason,
                    model_id=model_id,
                    license_name=license_name,
                    profile=profile,
                    territory=territory
                )

            # Profil recherche hors-ligne
            warning_msg = (
                f"[AVERTISSEMENT JURIDIQUE] Exécution de MiniMax H3 tolérée uniquement sous profil '{profile.value}' "
                f"à des fins de recherche et d'évaluation."
            )
            return GuardDecision(
                approved=True,
                status="WARNING",
                reason="Autorisé sous réserve d'un usage strictement non commercial de recherche.",
                model_id=model_id,
                license_name=license_name,
                profile=profile,
                territory=territory,
                warning_message=warning_msg
            )

        # Modèles sous licence permissive (Apache 2.0, MIT) ou Mock
        return GuardDecision(
            approved=True,
            status="APPROVED",
            reason="Licence standard compatible sans restriction territoriale identifiée.",
            model_id=model_id,
            license_name="Standard Open Source / Permissive",
            profile=profile,
            territory=territory
        )
