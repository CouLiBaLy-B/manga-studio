"""Adaptateur Mock pour la génération de clips vidéo (tests et exécution hors-ligne)."""

import os
from pathlib import Path
from typing import List, Optional
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import StoryboardSegment
from manga_studio.core.ports.video_generator import VideoGeneratorPort


class MockVideoGeneratorAdapter(VideoGeneratorPort):
    """Générateur de clips simulés pour tests unitaires et intégration locale rapide."""

    def generate_clip(
        self,
        segment: StoryboardSegment,
        reference_images: List[Path],
        output_path: Path,
        config: TalePipelineConfig,
        seed: Optional[int] = None
    ) -> Path:
        """Crée un fichier vidéo fictif ou généré localement représentant le segment."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # En mode test offline, nous écrivons un en-tête MP4 synthétique ou un conteneur valide
        header = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41"
        segment_info = f"Segment {segment.scene_id} - Duration: {segment.duree_s}s - Seed: {seed}".encode("utf-8")
        payload = header + b"\x00" * 256 + segment_info
        
        output_path.write_bytes(payload)
        return output_path
