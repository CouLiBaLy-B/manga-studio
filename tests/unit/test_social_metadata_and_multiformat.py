"""Tests unitaires pour le générateur de métadonnées sociales et l'exportateur multi-formats."""

import tempfile
from pathlib import Path
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    Storyboard,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.multiformat_exporter import MultiFormatExporter
from manga_studio.core.social_metadata import SocialMetadataGenerator


def create_sample_storyboard() -> Storyboard:
    seg = StoryboardSegment(
        ordre=1, scene_id="scene_001", titre="Le Départ de Râ", source_refs=[],
        frame="Râ monte à bord", characters_present=["ra"], reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Gardien", kind="dialogue", text="La route du ciel est prête.")],
        prompt_ia="Prompt. epic anime style", duree_s=6.0,
        emotion="épique", plan="low angle", decor="Nil", continuity_in="",
        continuity_out="", transition=TransitionConfig()
    )
    return Storyboard(schema_version="1.0", story_id="mythe_ra", segments=[seg])


def test_social_metadata_generator():
    """Vérifie la génération des packs de métadonnées pour TikTok, YouTube Shorts et Instagram."""
    extractor = RuleBasedCharacterExtractorAdapter()
    bible = extractor.extract_character_bible("mythe_ra", "Râ et les dieux", [Path("personnage_01.png")])
    sb = create_sample_storyboard()

    pkg = SocialMetadataGenerator.generate_package("mythe_ra", sb, bible)
    assert pkg.story_id == "mythe_ra"
    assert "Râ" in pkg.tiktok.viral_title
    assert len(pkg.tiktok.hashtags) >= 3
    assert "#Shorts" in pkg.youtube_shorts.description
    assert len(pkg.youtube_shorts.tags) >= 3
    assert "✨" in pkg.instagram_reels_caption


def test_multiformat_exporter_generation():
    """Vérifie l'export aux formats 9:16, 1:1 et 16:9."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        src_video = tmp_path / "final_video.mp4"
        src_video.write_bytes(b"\x00" * 512)

        out_dir = tmp_path / "formats"
        formats = MultiFormatExporter.export_all_formats(src_video, out_dir)

        assert "vertical_9_16" in formats
        assert "square_1_1" in formats
        assert "landscape_16_9" in formats

        for p in formats.values():
            assert p.exists()
            assert p.stat().st_size > 0
