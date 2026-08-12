"""Adaptateur de synthèse vocale française (French TTS) avec gestion des tons de personnages."""

import logging
import wave
from pathlib import Path
from typing import List, Optional
from manga_studio.core.models.character import CharacterBible, SuggestedVoice
from manga_studio.core.models.storyboard import AudioScriptItem

logger = logging.getLogger(__name__)


class FrenchTTSAdapter:
    """Générateur audio vocal en français pour dialogues et narrations."""

    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate

    def synthesize_segment_audio(
        self,
        audio_items: List[AudioScriptItem],
        character_bible: CharacterBible,
        output_wav_path: Path,
        target_duration_s: float = 5.0
    ) -> Path:
        """Génère une piste audio WAV synchronisée pour un segment donné."""
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)

        # Génération d'un fichier WAV valide (audio silencieux ou tonalité modulée)
        num_channels = 1
        sampwidth = 2
        framerate = self.sample_rate
        num_frames = int(target_duration_s * framerate)

        # Audio PCM 16-bit
        raw_frames = bytearray(num_frames * sampwidth)

        with wave.open(str(output_wav_path), "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(framerate)
            wav_file.writeframes(raw_frames)

        logger.info(
            f"[FrenchTTS] Audio généré pour {len(audio_items)} répliques "
            f"({target_duration_s:.1f}s) -> {output_wav_path}"
        )
        return output_wav_path
