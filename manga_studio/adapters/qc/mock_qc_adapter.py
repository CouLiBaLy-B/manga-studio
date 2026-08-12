"""Adaptateur Mock configurable pour les tests du Contrôle Qualité."""

from pathlib import Path
from typing import Dict, List, Optional
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.qc import QCReport, VisualSimilarityResult
from manga_studio.core.models.storyboard import StoryboardSegment
from manga_studio.core.ports.quality_evaluator import QualityEvaluatorPort


class MockQualityEvaluatorAdapter(QualityEvaluatorPort):
    """Évaluateur QC configurable permettant de simuler des succès, échecs ou révisions."""

    def __init__(
        self,
        force_status: Optional[str] = None,
        fail_attempts_count: int = 0,
        fixed_score: float = 0.85
    ):
        self.force_status = force_status
        self.fail_attempts_count = fail_attempts_count
        self.fixed_score = fixed_score

    def evaluate_clip(
        self,
        clip_path: Path,
        segment: StoryboardSegment,
        reference_images: List[Path],
        attempt: int,
        config: TalePipelineConfig
    ) -> QCReport:
        if self.force_status:
            rec = "accept" if self.force_status == "passed" else ("retry" if attempt <= config.max_qc_retries else "flag_review")
            return QCReport(
                segment_id=segment.scene_id,
                attempt=attempt,
                status=self.force_status,
                duration_ok=True,
                audio_present=True,
                dialogue_wer=0.04,
                visual_similarity=VisualSimilarityResult(model="mock_qc", score=self.fixed_score, threshold=config.qc_similarity_threshold),
                attribute_checks={"gold_robes_detected": True, "sun_disk_detected": True},
                issues=[] if self.force_status == "passed" else ["Mock issue"],
                recommendation=rec
            )

        # Simulation d'échec sur les premières tentatives si configuré
        if attempt <= self.fail_attempts_count:
            return QCReport(
                segment_id=segment.scene_id,
                attempt=attempt,
                status="failed",
                duration_ok=True,
                audio_present=True,
                dialogue_wer=0.25,
                visual_similarity=VisualSimilarityResult(model="mock_qc", score=0.60, threshold=config.qc_similarity_threshold),
                attribute_checks={"gold_robes_detected": False},
                issues=["Similarité visuelle insuffisante."],
                recommendation="retry" if attempt <= config.max_qc_retries else "flag_review"
            )

        return QCReport(
            segment_id=segment.scene_id,
            attempt=attempt,
            status="passed",
            duration_ok=True,
            audio_present=True,
            dialogue_wer=0.03,
            visual_similarity=VisualSimilarityResult(model="mock_qc", score=self.fixed_score, threshold=config.qc_similarity_threshold),
            attribute_checks={"gold_robes_detected": True, "sun_disk_detected": True},
            issues=[],
            recommendation="accept"
        )
