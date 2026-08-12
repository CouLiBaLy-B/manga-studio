"""Nœud 1 : Ingestion du conte et vérification des images de personnages."""

import uuid
from pathlib import Path
from typing import Dict
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.pipeline.state import TalePipelineState


class IngestionNode:
    """Valide les entrées, indexe les images de personnages et calcule leurs empreintes SHA-256."""

    def __init__(self, artifact_store: ArtifactStorePort):
        self.artifact_store = artifact_store

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        story_path = state["config"].story_path
        characters_dir = state["config"].characters_dir

        if not story_path.exists():
            raise FileNotFoundError(f"Fichier de conte introuvable : {story_path}")

        tale_text = story_path.read_text(encoding="utf-8")
        story_id = state.get("story_id") or story_path.stem

        # Recherche des images de personnages (1 à 9)
        image_paths = []
        if characters_dir.exists():
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                image_paths.extend(sorted(characters_dir.glob(ext)))

        image_store_map: Dict[str, Path] = {}
        for p in image_paths[:state["config"].max_reference_images]:
            image_store_map[p.name] = p

        # Journalisation de l'événement d'ingestion
        self.artifact_store.append_manifest_event(
            ManifestEvent(
                event_id=str(uuid.uuid4()),
                step="ingestion",
                action="ingest_inputs",
                status="SUCCESS",
                details={
                    "story_id": story_id,
                    "tale_length_chars": len(tale_text),
                    "characters_images_found": len(image_store_map),
                    "images": [
                        {"name": k, "sha256": self.artifact_store.compute_sha256(v)}
                        for k, v in image_store_map.items()
                    ]
                }
            )
        )

        state["story_id"] = story_id
        state["tale_text"] = tale_text
        state["image_paths"] = list(image_store_map.values())
        state["image_store_map"] = image_store_map
        return state
