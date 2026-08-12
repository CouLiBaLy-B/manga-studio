"""Port pour l'évaluation automatique de la qualité (QC) des clips."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.qc import QCReport
from manga_studio.core.models.storyboard import StoryboardSegment


class QualityEvaluatorPort(ABC):
    """Interface pour le contrôle qualité automatisé."""

    @abstractmethod
    def evaluate_clip(
        self,
        clip_path: Path,
        segment: StoryboardSegment,
        reference_images: List[Path],
        attempt: int,
        config: TalePipelineConfig
    ) -> QCReport:
        """Évalue la conformité visuelle, la durée et l'intégrité audio d'un clip."""
        pass
