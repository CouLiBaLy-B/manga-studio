"""Port pour le garde-fou de licences et conformité territoriale."""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from manga_studio.core.models.config import DeploymentProfile


class GuardDecision(BaseModel):
    """Décision formelle émise par le LicenseGuard."""
    approved: bool
    status: str  # "APPROVED", "BLOCKED", "WARNING"
    reason: str
    model_id: str
    license_name: str
    profile: DeploymentProfile
    territory: str
    warning_message: Optional[str] = None


class LicenseViolationError(Exception):
    """Exception levée en cas de violation de licence ou restriction territoriale."""
    pass


class LicenseGuardPort(ABC):
    """Interface pour le garde-fou des licences."""

    @abstractmethod
    def validate_execution(
        self,
        model_id: str,
        profile: DeploymentProfile,
        territory: str,
        allow_local_flag: bool = False
    ) -> GuardDecision:
        """Valide si l'exécution du modèle est licite selon le profil et le territoire."""
        pass
