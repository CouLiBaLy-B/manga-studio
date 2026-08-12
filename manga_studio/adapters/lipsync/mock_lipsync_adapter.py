"""Adaptateur Mock pour la synchronisation labiale (tests hors-ligne)."""

from pathlib import Path
from typing import Optional, Tuple
from manga_studio.core.ports.lipsync import LipSyncPort


class MockLipSyncAdapter(LipSyncPort):
    """Simulateur de synchronisation labiale pour tests unitaires."""

    def apply_lipsync(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        face_crop_box: Optional[Tuple[int, int, int, int]] = None
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        header = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41"
        info = f"MockLipSync - Video:{video_path.name} - Audio:{audio_path.name}".encode("utf-8")
        output_path.write_bytes(header + b"\x00" * 256 + info)
        return output_path
