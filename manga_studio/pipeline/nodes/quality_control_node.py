"""Nœud 5 : Évaluation du Contrôle Qualité (QC) et gestion du retry borné."""

import uuid
from typing import Dict, List
from manga_studio.core.models.manifest import ManifestEvent
from manga_studio.core.models.qc import QCReport
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.core.ports.quality_evaluator import QualityEvaluatorPort
from manga_studio.pipeline.state import TalePipelineState


class QualityControlNode:
    """Évalue la qualité des clips et orchestre les régénérations bornées (max 2 retries)."""

    def __init__(
        self,
        quality_evaluator: QualityEvaluatorPort,
        artifact_store: ArtifactStorePort
    ):
        self.quality_evaluator = quality_evaluator
        self.artifact_store = artifact_store

    def execute(self, state: TalePipelineState) -> TalePipelineState:
        storyboard = state["validated_storyboard"]
        clip_paths = state["clip_paths"]
        bible = state["character_bible"]
        image_store_map = state["image_store_map"]
        config = state["config"]

        qc_reports: Dict[str, QCReport] = state.get("qc_reports", {})
        retry_counts = state.get("retry_counts", {})
        segments_needing_retry = []

        for seg in storyboard.segments:
            clip_path = clip_paths.get(seg.scene_id)
            if not clip_path or not clip_path.exists():
                continue

            attempt = retry_counts.get(seg.scene_id, 1)

            # Évaluation QC
            report = self.quality_evaluator.evaluate_clip(
                clip_path=clip_path,
                segment=seg,
                reference_images=list(image_store_map.values()),
                attempt=attempt,
                config=config
            )

            # Persistance du rapport QC unitaire (qc/001.json)
            qc_filename = f"{seg.ordre:03d}.json"
            self.artifact_store.save_json(f"qc/{qc_filename}", report)
            qc_reports[seg.scene_id] = report

            # Journalisation manifest
            self.artifact_store.append_manifest_event(
                ManifestEvent(
                    event_id=str(uuid.uuid4()),
                    step="quality_control",
                    action="evaluate_segment_qc",
                    status="SUCCESS" if report.status == "passed" else ("WARNING" if report.status == "needs_review" else "FAILED"),
                    details={
                        "scene_id": seg.scene_id,
                        "attempt": attempt,
                        "qc_status": report.status,
                        "similarity_score": report.visual_similarity.score,
                        "dialogue_wer": report.dialogue_wer,
                        "recommendation": report.recommendation,
                        "issues": report.issues
                    }
                )
            )

            if report.status == "failed" and attempt <= config.max_qc_retries:
                segments_needing_retry.append(seg.scene_id)

        state["qc_reports"] = qc_reports
        return state
