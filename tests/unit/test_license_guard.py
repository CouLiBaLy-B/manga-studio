"""Tests unitaires pour le LicenseGuard et le refus commercial en territoire exclu."""

import pytest
from manga_studio.adapters.guard.license_guard_adapter import LicenseGuardAdapter
from manga_studio.core.models.config import DeploymentProfile
from manga_studio.core.ports.license_guard import LicenseViolationError


def test_license_guard_blocks_commercial_h3_in_eu():
    """Vérifie que l'exécution locale commerciale de MiniMax H3 en UE est strictement refusée."""
    guard = LicenseGuardAdapter()
    
    with pytest.raises(LicenseViolationError) as exc_info:
        guard.validate_execution(
            model_id="minimax_h3_ref2va",
            profile=DeploymentProfile.COMMERCIAL,
            territory="EU",
            allow_local_flag=True
        )
    assert "VIOLATION DE LICENCE" in str(exc_info.value)
    assert "EU" in str(exc_info.value)


def test_license_guard_blocks_commercial_h3_in_us():
    """Vérifie le blocage commercial de H3 aux USA."""
    guard = LicenseGuardAdapter()
    with pytest.raises(LicenseViolationError):
        guard.validate_execution(
            model_id="minimax_h3_ref2va",
            profile=DeploymentProfile.COMMERCIAL,
            territory="US",
            allow_local_flag=True
        )


def test_license_guard_requires_explicit_local_flag():
    """Vérifie que sans flag explicite ENABLE_H3_LOCAL, H3 est bloqué."""
    guard = LicenseGuardAdapter()
    decision = guard.validate_execution(
        model_id="minimax_h3_ref2va",
        profile=DeploymentProfile.RESEARCH,
        territory="JP",
        allow_local_flag=False
    )
    assert decision.approved is False
    assert decision.status == "BLOCKED"


def test_license_guard_allows_research_profile_with_warning():
    """Vérifie que le profil recherche avec flag explicite émet un avertissement légal."""
    guard = LicenseGuardAdapter()
    decision = guard.validate_execution(
        model_id="minimax_h3_ref2va",
        profile=DeploymentProfile.RESEARCH,
        territory="JP",
        allow_local_flag=True
    )
    assert decision.approved is True
    assert decision.status == "WARNING"
    assert decision.warning_message is not None


def test_license_guard_approves_permissive_models():
    """Vérifie l'approbation sans restriction des modèles sous licence permissive (Apache 2.0 / Mock)."""
    guard = LicenseGuardAdapter()
    decision = guard.validate_execution(
        model_id="wan_2_1_14b",
        profile=DeploymentProfile.COMMERCIAL,
        territory="EU",
        allow_local_flag=True
    )
    assert decision.approved is True
    assert decision.status == "APPROVED"
