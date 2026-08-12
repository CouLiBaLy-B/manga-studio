"""Concepteur sonore et mixeur audio avec Ducking dynamique pour la musique et l'ambiance."""

import wave
from pathlib import Path
from typing import Dict, List, Optional
from manga_studio.core.models.storyboard import StoryboardSegment


class AudioSoundDesigner:
    """Génère et mixe les pistes d'ambiance et de musique avec ducking automatique."""

    EMOTION_SOUNDSCAPES = {
        "épique": {"bpm": 120, "key": "D minor", "ambience": "sacred_choir_brass"},
        "solennel": {"bpm": 90, "key": "A minor", "ambience": "temple_bells_wind"},
        "mystique": {"bpm": 75, "key": "C minor", "ambience": "nile_night_whispers"},
        "neutre": {"bpm": 100, "key": "G major", "ambience": "ancient_ambient_harp"}
    }

    @classmethod
    def generate_ambient_track(
        cls,
        segments: List[StoryboardSegment],
        output_wav_path: Path,
        sample_rate: int = 24000
    ) -> Path:
        """Génère une piste sonore d'ambiance continue pour l'ensemble du conte."""
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        total_duration_s = sum(s.duree_s for s in segments)
        num_frames = int(total_duration_s * sample_rate)

        # Génération d'une onde sinusoïdale d'ambiance douce (binaural drone 432 Hz)
        raw_bytes = bytearray()
        import math
        for i in range(num_frames):
            t = i / sample_rate
            # Mix doux de deux fréquences d'ambiance
            val = int(1200 * math.sin(2 * math.pi * 108.0 * t) + 800 * math.sin(2 * math.pi * 216.0 * t))
            clamped = max(-32768, min(32767, val))
            # Format PCM 16-bit little endian
            raw_bytes.extend(clamped.to_bytes(2, byteorder="little", signed=True))

        with wave.open(str(output_wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(raw_bytes)

        return output_wav_path

    @classmethod
    def build_ducking_filter_complex(
        cls,
        voice_stream_label: str = "1:a",
        bgm_stream_label: str = "2:a",
        ducking_attenuation_db: float = -14.0
    ) -> str:
        """Génère la chaîne de filtre FFmpeg pour le ducking automatique (sidechaincompress)."""
        # sidechaincompress : compresse la BGM dès que la voix dépasse un seuil
        return (
            f"[{bgm_stream_label}][{voice_stream_label}]"
            f"sidechaincompress=threshold=0.08:ratio=5:attack=10:release=250[ducked_bgm];"
            f"[{voice_stream_label}][ducked_bgm]amix=inputs=2:duration=first:weights=1.0 0.4[aout]"
        )
