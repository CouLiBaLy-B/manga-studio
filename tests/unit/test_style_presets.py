"""Tests unitaires pour la bibliothèque de presets stylistiques manga."""

from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.style_presets import StylePresetRegistry


def test_style_preset_lookup():
    """Vérifie la récupération des différents styles manga."""
    shonen = StylePresetRegistry.get_preset("shonen_epic")
    assert shonen.name == "Shōnen Épique"
    assert "shonen anime style" in shonen.prompt_suffix

    ghibli = StylePresetRegistry.get_preset("ghibli_poetic")
    assert "Studio Ghibli" in ghibli.prompt_suffix

    seinen = StylePresetRegistry.get_preset("seinen_dark_fantasy")
    assert "chiaroscuro" in seinen.prompt_suffix


def test_style_preset_fallback():
    """Vérifie le repli sur le style mythologie en cas de clé inconnue."""
    unknown = StylePresetRegistry.get_preset("style_inexistant")
    assert unknown.key == "watercolor_mythology"


def test_style_presets_list():
    """Vérifie le catalogue complet des presets disponibles."""
    presets = StylePresetRegistry.list_presets()
    assert len(presets) >= 5
    assert "cyberpunk_neo_tokyo" in presets
