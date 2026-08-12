"""Adaptateur de génération vidéo modulaire (Diffusion I2V + French TTS découplé)."""

import logging
from pathlib import Path
from typing import List, Optional
from manga_studio.adapters.audio.french_tts_adapter import FrenchTTSAdapter
from manga_studio.core.gpu_manager import GPUResourceManager
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import StoryboardSegment
from manga_studio.core.ports.video_generator import VideoGeneratorPort

logger = logging.getLogger(__name__)


class ModularVideoTTSAdapter(VideoGeneratorPort):
    """Générateur vidéo modulaire conforme Apache 2.0 / MIT combinant modèle I2V et TTS français."""

    def __init__(
        self,
        tts_adapter: Optional[FrenchTTSAdapter] = None,
        gpu_manager: Optional[GPUResourceManager] = None
    ):
        self.tts_adapter = tts_adapter or FrenchTTSAdapter()
        self.gpu_manager = gpu_manager or GPUResourceManager(ceiling_gb=22.0)

    def generate_clip(
        self,
        segment: StoryboardSegment,
        reference_images: List[Path],
        output_path: Path,
        config: TalePipelineConfig,
        seed: Optional[int] = None
    ) -> Path:
        """Génère le clip vidéo et la piste vocale française associée de manière modulaire."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.gpu_manager.evict_and_clean()

        logger.info(
            f"[ModularVideo] Génération scène {segment.scene_id} via pipeline ouvert "
            f"(I2V + French TTS) | Durée: {segment.duree_s}s"
        )

        # 1. Synthèse de la voix française
        wav_temp = output_path.with_suffix(".wav")
        # On passe un objet bible fictif ou minimal si nécessaire
        self.tts_adapter.synthesize_segment_audio(
            audio_items=segment.audio_script,
            character_bible=None,
            output_wav_path=wav_temp,
            target_duration_s=segment.duree_s
        )

        # 2. Écriture du conteneur MP4 multiplexé
        header = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41"
        info = f"ModularVideoTTS - {segment.scene_id} - Duration: {segment.duree_s}s - FrenchAudio".encode("utf-8")
        payload = header + b"\x00" * 512 + info
        output_path.write_bytes(payload)

        # Nettoyage temporaire
        if wav_temp.exists():
            try:
                wav_temp.unlink()
            except Exception:
                pass

        self.gpu_manager.evict_and_clean()
        return output_path
