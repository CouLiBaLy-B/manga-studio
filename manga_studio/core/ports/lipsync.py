"""Port pour le module de synchronisation labiale (LipSync)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple


class LipSyncPort(ABC):
    """Interface abstraite pour l'alignement des mouvements labiaux sur l'audio."""

    @abstractmethod
    def apply_lipsync(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        face_crop_box: Optional[Tuple[int, int, int, int]] = None
    ) -> Path:
        """Applique la synchronisation labiale sur le visage du personnage parlant."""
        pass
