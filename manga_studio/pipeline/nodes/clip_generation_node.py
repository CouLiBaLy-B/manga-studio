"""Nœud 4 : Génération séquentielle des clips vidéo avec contrôle VRAM."""

import uuid
from pathlib import Path
from typing import Dict, List
from manga_studio.core.gpu_manager import GPUResourceManager
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.core.ports.reference_selector import ReferenceSelectorPort
from manga_studio.core.ports.video_generator import VideoGeneratorPort
from manga_studio.pipeline.state import TalePipelineState


class ClipGenerationNode:
    """Génère séquentiellement les clips vidéo avec isolation GPU et sélection déterministe des références."""

    def __init__(
        self,
        video_generator: VideoGeneratorPort,
        reference_selector: ReferenceSelectorPort,
        artifact_store: ArtifactStorePort,
        gpu_manager: GPUResourceManager
    ):
        self.video_generator = video_generator
        self.reference_selector = reference_selector
        self.artifact_store = artifact_store
        self.gpu_manager = gpu_manager

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        storyboard = state["validated_storyboard"]
        bible = state["character_bible"]
        image_store_map = state["image_store_map"]
        config = state["config"]

        clip_paths: Dict[str, Path] = state.get("clip_paths", {})
        retry_counts = state.get("retry_counts", {})

        for seg in storyboard.segments:
            # Si le clip a déjà passé le QC, on ne le régénère pas
            if seg.scene_id in clip_paths and state.get("qc_reports", {}).get(seg.scene_id, {}).status == "passed":
                continue

            current_attempt = retry_counts.get(seg.scene_id, 0) + 1
            retry_counts[seg.scene_id] = current_attempt

            # 1. Sélection des références pour le segment
            ref_paths = self.reference_selector.select_references_for_segment(
                segment=seg,
                character_bible=bible,
                image_store_map=image_store_map,
                max_references=config.max_reference_images
            )

            # 2. Chemin cible du clip
            clip_name = f"{seg.ordre:03d}.mp4"
            clip_target_path = self.artifact_store.root_dir / "clips" / clip_name

            # 3. Isolation GPU avant inférence
            self.gpu_manager.evict_and_clean()

            # 4. Génération du clip
            seed = (config.seed or 42) + seg.ordre + (current_attempt * 100)
            generated_path = self.video_generator.generate_clip(
                segment=seg,
                reference_images=ref_paths,
                output_path=clip_target_path,
                config=config,
                seed=seed
            )

            clip_paths[seg.scene_id] = generated_path

            # 5. Journalisation manifest
            self.artifact_store.append_manifest_event(
                ManifestEvent(
                    event_id=str(uuid.uuid4()),
                    step="clip_generation",
                    action="generate_segment_clip",
                    status="SUCCESS",
                    details={
                        "scene_id": seg.scene_id,
                        "ordre": seg.ordre,
                        "attempt": current_attempt,
                        "seed": seed,
                        "references_used": [p.name for p in ref_paths],
                        "sha256": self.artifact_store.compute_sha256(generated_path)
                    }
                )
            )

        state["clip_paths"] = clip_paths
        state["retry_counts"] = retry_counts
        return state
