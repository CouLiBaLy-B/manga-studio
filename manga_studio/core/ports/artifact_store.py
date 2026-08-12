"""Port pour la gestion immuable et le stockage des artefacts de génération."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from manga_studio.core.models.manifest import ManifestEvent, RunReport


class ArtifactStorePort(ABC):
    """Interface pour le stockage et l'indexation des artefacts du pipeline."""

    @abstractmethod
    def initialize_store(self, output_dir: Path, story_id: str) -> Path:
        """Initialise l'arborescence standard du run."""
        pass

    @abstractmethod
    def save_json(self, rel_path: str, data: Any) -> Path:
        """Sauvegarde un objet sérialisable en JSON."""
        pass

    @abstractmethod
    def append_manifest_event(self, event: ManifestEvent) -> None:
        """Ajoute un événement au fichier render_manifest.jsonl."""
        pass

    @abstractmethod
    def save_run_report(self, report: RunReport) -> Path:
        """Sauvegarde le rapport final run_report.json."""
        pass

    @abstractmethod
    def compute_sha256(self, file_path: Path) -> str:
        """Calcule l'empreinte SHA-256 d'un fichier."""
        pass
