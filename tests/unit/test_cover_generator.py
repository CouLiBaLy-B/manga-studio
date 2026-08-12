"""Tests unitaires pour le générateur d'affiches et de vignettes (Cover & Posters)."""

import tempfile
from pathlib import Path
from PIL import Image
from manga_studio.core.cover_generator import CoverPosterGenerator


def test_cover_poster_generator():
    """Vérifie la génération d'une affiche verticale 1080x1920 avec dégradé et titre."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        char_img = tmp_path / "char.png"
        out_poster = tmp_path / "poster.png"

        # Image de personnage fictive
        Image.new("RGB", (300, 300), color=(244, 197, 66)).save(char_img)

        res = CoverPosterGenerator.generate_cover_poster(
            title="Le Mythe Sacré de Râ",
            character_image_path=char_img,
            output_path=out_poster,
            size=(1080, 1920)
        )

        assert res.exists()
        with Image.open(res) as img:
            assert img.size == (1080, 1920)
