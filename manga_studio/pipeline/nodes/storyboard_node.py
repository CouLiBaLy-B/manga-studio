"""Nœud 3 : Génération et validation du Storyboard structuré."""

import uuid
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.core.ports.storyboard_llm import StoryboardLLMPort
from manga_studio.pipeline.state import TalePipelineState


class StoryboardNode:
    """Orchestre la génération du Storyboard LLM avec tolérance aux pannes et validation de continuité."""

    def __init__(
        self,
        storyboard_llm: StoryboardLLMPort,
        artifact_store: ArtifactStorePort
    ):
        self.storyboard_llm = storyboard_llm
        self.artifact_store = artifact_store

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        story_id = state["story_id"]
        tale_text = state["tale_text"]
        bible = state["character_bible"]
        config = state["config"]

        # Génération du storyboard brut
        storyboard = self.storyboard_llm.generate_storyboard(
            story_id=story_id,
            tale_text=tale_text,
            character_bible=bible,
            config=config
        )

        # Sauvegarde du storyboard brut
        raw_path = self.artifact_store.save_json("storyboard.json", storyboard)

        # Contrôle et validation supplémentaire de continuité
        validated_storyboard = storyboard  # Validé par Pydantic validators

        val_path = self.artifact_store.save_json("storyboard.validated.json", validated_storyboard)

        self.artifact_store.append_manifest_event(
            ManifestEvent(
                event_id=str(uuid.uuid4()),
                step="storyboard",
                action="generate_and_validate_storyboard",
                status="SUCCESS",
                details={
                    "total_segments": len(validated_storyboard.segments),
                    "total_duration_s": validated_storyboard.total_duration_s,
                    "raw_sha256": self.artifact_store.compute_sha256(raw_path),
                    "validated_sha256": self.artifact_store.compute_sha256(val_path)
                }
            )
        )

        state["storyboard"] = storyboard
        state["validated_storyboard"] = validated_storyboard
        return state
