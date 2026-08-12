"""Tests unitaires pour les sous-titres cinétiques TikTok (ASS enrichi)."""

from manga_studio.core.kinetic_subtitles import KineticSubtitleGenerator
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)


def test_kinetic_subtitles_keyword_highlighting():
    """Vérifie la mise en valeur automatique des mots clés."""
    raw_text = "Le soleil sacré de Râ éclaire la nuit éternelle."
    highlighted = KineticSubtitleGenerator._highlight_keywords(raw_text)
    assert "{\\c&H0042C5F4&}soleil{\\c&H00FFFFFF&}" in highlighted
    assert "{\\c&H0042C5F4&}Râ{\\c&H00FFFFFF&}" in highlighted


def test_kinetic_ass_generation():
    """Vérifie la génération complète du script ASS cinétique."""
    seg = StoryboardSegment(
        ordre=1, scene_id="scene_001", titre="Scène 1", source_refs=[],
        frame="Action", characters_present=["ra"], reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="La lumière est éternelle.")],
        prompt_ia="Prompt. epic anime style", duree_s=5.0,
        emotion="épique", plan="medium", decor="palais", continuity_in="",
        continuity_out="", transition=TransitionConfig()
    )

    ass_text = KineticSubtitleGenerator.generate_kinetic_ass([seg], title="Mythe Solaire")
    assert "[Script Info]" in ass_text
    assert "KineticMain" in ass_text
    assert "SpeakerTag" in ass_text
    assert "RÂ" in ass_text
