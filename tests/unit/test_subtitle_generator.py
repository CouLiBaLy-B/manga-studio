"""Tests unitaires pour la génération des sous-titres SRT et ASS synchronisés."""

from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.subtitle_generator import SubtitleGenerator


def test_subtitle_generator_srt_format():
    """Vérifie la génération de sous-titres au format SubRip (.srt)."""
    seg1 = StoryboardSegment(
        ordre=1,
        scene_id="scene_001",
        titre="Scène 1",
        source_refs=[],
        frame="Râ parle",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[
            AudioScriptItem(speaker="Gardien", kind="dialogue", text="La route du ciel est prête."),
            AudioScriptItem(speaker="Râ", kind="dialogue", text="Que la lumière soit.")
        ],
        prompt_ia="Prompt. epic anime style",
        duree_s=6.0,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )

    srt_out = SubtitleGenerator.generate_srt([seg1])
    assert "1" in srt_out
    assert "00:00:00,000 --> 00:00:03,000" in srt_out
    assert "[Gardien] La route du ciel est prête." in srt_out
    assert "00:00:03,000 --> 00:00:06,000" in srt_out
    assert "[Râ] Que la lumière soit." in srt_out


def test_subtitle_generator_ass_format():
    """Vérifie la génération au format Advanced SubStation Alpha (.ass)."""
    seg1 = StoryboardSegment(
        ordre=1,
        scene_id="scene_001",
        titre="Scène 1",
        source_refs=[],
        frame="Action",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="Réplique sacrée.")],
        prompt_ia="Prompt. epic anime style",
        duree_s=4.0,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )

    ass_out = SubtitleGenerator.generate_ass([seg1], title="Test Myth")
    assert "[Script Info]" in ass_out
    assert "PlayResX: 1080" in ass_out
    assert "PlayResY: 1920" in ass_out
    assert "Dialogue: 0,0:00:00.00,0:00:04.00" in ass_out
    assert "Réplique sacrée." in ass_out
