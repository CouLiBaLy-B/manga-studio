"""Nœud 2 : Extraction et verrouillage de la Bible des personnages."""

import uuid
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.core.ports.character_extractor import CharacterSheetExtractorPort
from manga_studio.pipeline.state import TalePipelineState


class CharacterBibleNode:
    """Extrait les fiches personnages canoniques, les verrouille et les persiste."""

    def __init__(
        self,
        extractor: CharacterSheetExtractorPort,
        artifact_store: ArtifactStorePort
    ):
        self.extractor = extractor
        self.artifact_store = artifact_store

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        story_id = state["story_id"]
        tale_text = state["tale_text"]
        image_paths = state["image_paths"]

        bible = self.extractor.extract_character_bible(
            story_id=story_id,
            tale_text=tale_text,
            image_paths=image_paths,
            locked=True
        )

        # Sauvegarde immuable du fichier character_bible.json
        saved_path = self.artifact_store.save_json("character_bible.json", bible)

        self.artifact_store.append_manifest_event(
            ManifestEvent(
                event_id=str(uuid.uuid4()),
                step="bible",
                action="extract_and_lock_character_bible",
                status="SUCCESS",
                details={
                    "characters_count": len(bible.characters),
                    "character_ids": [c.character_id for c in bible.characters],
                    "locked": bible.locked,
                    "sha256": self.artifact_store.compute_sha256(saved_path)
                }
            )
        )

        state["character_bible"] = bible
        return state
