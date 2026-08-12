"""Port pour le registre des modèles IA et métadonnées de licences."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Métadonnées descriptives d'un modèle IA."""
    model_id: str
    family: str
    version: str
    license_name: str
    license_url: str
    verification_date: str
    status: str = Field(default="VERIFIED", description="VERIFIED, UNVERIFIED, CONTRADICTED, ASSUMPTION")
    excluded_territories: List[str] = Field(default_factory=list)
    commercial_allowed: bool = True
    vram_requirement_gb: float = 0.0
    notes: str = ""


class ModelRegistryPort(ABC):
    """Interface pour le registre de modèles."""

    @abstractmethod
    def register_model(self, metadata: ModelMetadata) -> None:
        """Enregistre un modèle dans le catalogue."""
        pass

    @abstractmethod
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Récupère les métadonnées d'un modèle par son identifiant."""
        pass

    @abstractmethod
    def list_models(self) -> Dict[str, ModelMetadata]:
        """Retourne tous les modèles enregistrés."""
        pass
