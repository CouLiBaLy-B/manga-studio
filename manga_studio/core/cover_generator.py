"""Générateur de couvertures et affiches de conte (Thumbnails 9:16 et 16:9)."""

from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw


class CoverPosterGenerator:
    """Compose des affiches et vignettes percutantes pour TikTok et YouTube Shorts."""

    @classmethod
    def generate_cover_poster(
        cls,
        title: str,
        character_image_path: Optional[Path],
        output_path: Path,
        size: Tuple[int, int] = (1080, 1920),
        subtitle: str = "MangaTok Studio — Conte Animé"
    ) -> Path:
        """Génère une affiche verticale avec dégradé d'ambiance et titre stylisé."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        width, height = size

        # 1. Fond sombre de base
        poster = Image.new("RGB", (width, height), color=(15, 17, 26))
        draw = ImageDraw.Draw(poster)

        # 2. Incrustation du personnage si fourni
        if character_image_path and character_image_path.exists():
            with Image.open(character_image_path) as char_img:
                char_rgb = char_img.convert("RGB")
                char_resized = char_rgb.resize((width, int(height * 0.75)), Image.Resampling.LANCZOS)
                poster.paste(char_resized, (0, 0))

        # 3. Dégradé sombre en bas pour lisibilité
        gradient_height = int(height * 0.45)
        for y in range(gradient_height):
            alpha = int(255 * (y / gradient_height))
            y_pos = height - gradient_height + y
            draw.line([(0, y_pos), (width, y_pos)], fill=(9, 10, 15))

        # 4. Bordure et cadre doré
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(244, 197, 66), width=4)

        # 5. Textes et badges
        draw.rectangle([(40, 40), (320, 90)], fill=(244, 197, 66))
        draw.text((55, 55), "MANGA TOK STUDIO", fill=(0, 0, 0))

        # Titre en bas
        draw.text((60, height - 260), title[:35].upper(), fill=(244, 197, 66))
        draw.text((60, height - 180), subtitle, fill=(200, 200, 200))

        poster.save(output_path, "PNG", optimize=True)
        return output_path
