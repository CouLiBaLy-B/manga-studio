"""Tests unitaires pour le concepteur sonore et le mixage avec Ducking."""

import tempfile
from pathlib import Path
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.sound_designer import AudioSoundDesigner


def test_sound_designer_ambient_track_generation():
    """Vérifie la génération d'une piste d'ambiance continue en WAV."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_wav = Path(tmp_dir) / "ambient_bgm.wav"
        seg = StoryboardSegment(
            ordre=1, scene_id="scene_001", titre="Scène 1", source_refs=[],
            frame="Action", characters_present=["ra"], reference_character_ids=["ra"],
            audio_script=[], prompt_ia="Prompt. epic anime style", duree_s=3.0,
            emotion="épique", plan="medium", decor="palais", continuity_in="",
            continuity_out="", transition=TransitionConfig()
        )

        res = AudioSoundDesigner.generate_ambient_track([seg], out_wav, sample_rate=16000)
        assert res.exists()
        assert res.stat().st_size > 0


def test_sound_designer_ducking_filter_complex():
    """Vérifie la construction de la formule de ducking FFmpeg."""
    filter_str = AudioSoundDesigner.build_ducking_filter_complex("1:a", "2:a", ducking_attenuation_db=-14.0)
    assert "sidechaincompress" in filter_str
    assert "amix=inputs=2" in filter_str
