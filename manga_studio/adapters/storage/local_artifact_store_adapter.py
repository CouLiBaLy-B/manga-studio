"""Adaptateur de stockage local des artefacts et des journaux d'exécution."""

import hashlib
import json
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
from manga_studio.core.models.manifest import ManifestEvent, RunReport
from manga_studio.core.ports.artifact_store import ArtifactStorePort


class LocalArtifactStoreAdapter(ArtifactStorePort):
    """Gère l'arborescence des fichiers générés et garantit la traçabilité par manifest."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir

    def initialize_store(self, output_dir: Path, story_id: str) -> Path:
        """Crée l'arborescence standardisée pour le run."""
        self.root_dir = output_dir
        
        # Création des sous-dossiers
        (self.root_dir / "clips").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "qc").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "subtitles").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "manifests").mkdir(parents=True, exist_ok=True)

        return self.root_dir

    def save_json(self, rel_path: str, data: Any) -> Path:
        """Enregistre un objet ou un modèle Pydantic au format JSON indenté."""
        if not self.root_dir:
            raise RuntimeError("Le store d'artefacts n'a pas été initialisé via initialize_store.")

        target = self.root_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, BaseModel):
            content = data.model_dump_json(indent=2)
        elif isinstance(data, (dict, list)):
            content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            content = str(data)

        target.write_text(content, encoding="utf-8")
        return target

    def append_manifest_event(self, event: ManifestEvent) -> None:
        """Ajoute une ligne JSONL au manifest render_manifest.jsonl."""
        if not self.root_dir:
            raise RuntimeError("Le store d'artefacts n'a pas été initialisé.")

        manifest_path = self.root_dir / "manifests" / "render_manifest.jsonl"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        line = event.model_dump_json() + "\n"
        with manifest_path.open("a", encoding="utf-8") as f:
            f.write(line)

    def save_run_report(self, report: RunReport) -> Path:
        """Enregistre le rapport final run_report.json."""
        return self.save_json("manifests/run_report.json", report)

    def compute_sha256(self, file_path: Path) -> str:
        """Calcule l'empreinte SHA-256 d'un fichier binaire ou textuel."""
        if not file_path.exists():
            return ""
        hasher = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
