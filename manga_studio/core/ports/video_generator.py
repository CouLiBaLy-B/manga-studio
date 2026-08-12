"""Port pour la génération de clips vidéo unitaires."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import StoryboardSegment


class VideoGeneratorPort(ABC):
    """Interface pour les générateurs de clips vidéo et audio conjointe."""

    @abstractmethod
    def generate_clip(
        self,
        segment: StoryboardSegment,
        reference_images: List[Path],
        output_path: Path,
        config: TalePipelineConfig,
        seed: Optional[int] = None
    ) -> Path:
        """Génère un clip vidéo MP4 pour le segment donné."""
        pass
