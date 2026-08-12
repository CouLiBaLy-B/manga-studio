"""Tests unitaires pour l'adaptateur vidéo modulaire et la synthèse vocale française."""

import tempfile
from pathlib import Path
from manga_studio.adapters.audio.french_tts_adapter import FrenchTTSAdapter
from manga_studio.adapters.video.modular_video_tts_adapter import ModularVideoTTSAdapter
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)


def test_french_tts_adapter_wav_generation():
    """Vérifie la génération d'un fichier audio WAV synchronisé."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_wav = Path(tmp_dir) / "test_speech.wav"
        tts = FrenchTTSAdapter()
        items = [AudioScriptItem(speaker="Râ", kind="dialogue", text="Bonjour")]
        
        res = tts.synthesize_segment_audio(items, None, out_wav, target_duration_s=2.5)
        assert res.exists()
        assert res.stat().st_size > 0


def test_modular_video_tts_adapter_clip_generation():
    """Vérifie la génération d'un clip vidéo multiplexé avec audio français."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_mp4 = Path(tmp_dir) / "modular_clip.mp4"
        adapter = ModularVideoTTSAdapter()

        seg = StoryboardSegment(
            ordre=1, scene_id="scene_001", titre="Scène 1", source_refs=[],
            frame="Action", characters_present=["ra"], reference_character_ids=["ra"],
            audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="Texte français")],
            prompt_ia="Modular action prompt. epic anime style", duree_s=4.0,
            emotion="épique", plan="medium", decor="palais", continuity_in="",
            continuity_out="", transition=TransitionConfig()
        )

        config = TalePipelineConfig(
            story_path=Path("tests/fixtures/conte.txt"),
            characters_dir=Path("tests/fixtures/personnages")
        )

        res = adapter.generate_clip(seg, [], out_mp4, config)
        assert res.exists()
        assert res.stat().st_size > 0
