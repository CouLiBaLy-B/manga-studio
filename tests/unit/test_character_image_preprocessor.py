"""Tests unitaires pour le préprocesseur d'images de personnages."""

import tempfile
from pathlib import Path
from PIL import Image
from manga_studio.core.image_preprocessor import CharacterImagePreprocessor


def test_character_image_preprocessor_normalization_and_palette():
    """Vérifie le redimensionnement et l'extraction de la palette hexadécimale."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        src_img_path = tmp_path / "raw_char.png"
        out_img_path = tmp_path / "norm_char.png"

        # Création d'une image de test avec dominantes dorées
        img = Image.new("RGB", (800, 600), color=(244, 197, 66))
        img.save(src_img_path)

        result = CharacterImagePreprocessor.inspect_and_normalize_image(
            image_path=src_img_path,
            output_path=out_img_path,
            target_size=(512, 512)
        )

        assert out_img_path.exists()
        assert result["normalized_dimensions"] == (512, 512)
        assert len(result["dominant_hex_colors"]) >= 1
        assert result["dominant_hex_colors"][0].startswith("#")
