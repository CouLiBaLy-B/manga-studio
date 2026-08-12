"""Port pour l'assemblage vidéo et audio final avec FFmpeg."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import StoryboardSegment


class VideoAssemblerPort(ABC):
    """Interface pour l'assemblage déterministe des clips et pistes audio."""

    @abstractmethod
    def assemble(
        self,
        clip_paths: List[Path],
        segments: List[StoryboardSegment],
        output_video_path: Path,
        config: TalePipelineConfig,
        subtitles_path: Optional[Path] = None
    ) -> Path:
        """Assemble les clips séquentiels en une vidéo verticale normalisée EBU R128."""
        pass
