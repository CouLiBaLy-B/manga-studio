"""Préprocesseur d'images de personnages (recadrage, normalisation et extraction de palette)."""

from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image


class CharacterImagePreprocessor:
    """Normalise et prépare les images de référence pour les modèles vidéo et de vision."""

    @staticmethod
    def inspect_and_normalize_image(
        image_path: Path,
        output_path: Path,
        target_size: Tuple[int, int] = (512, 512)
    ) -> Dict[str, any]:
        """Redimensionne proprement l'image de référence et extrait sa palette de couleurs."""
        if not image_path.exists():
            raise FileNotFoundError(f"Image source introuvable : {image_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(image_path) as img:
            img_rgb = img.convert("RGB")
            
            # Recadrage centré proportionnel (Square ou 9:16)
            orig_w, orig_h = img_rgb.size
            min_dim = min(orig_w, orig_h)
            left = (orig_w - min_dim) // 2
            top = (orig_h - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            
            cropped = img_rgb.crop((left, top, right, bottom))
            resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
            resized.save(output_path, "PNG", optimize=True)

            # Extraction de la palette dominante (couleurs dominantes en hexadécimal)
            dominant_colors = CharacterImagePreprocessor._extract_dominant_colors(resized, num_colors=3)

        return {
            "original_dimensions": (orig_w, orig_h),
            "normalized_dimensions": target_size,
            "normalized_path": str(output_path),
            "dominant_hex_colors": dominant_colors
        }

    @staticmethod
    def _extract_dominant_colors(img: Image.Image, num_colors: int = 3) -> List[str]:
        """Extrait les couleurs hexadécimales dominantes d'une image PIL."""
        quantized = img.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()[:num_colors * 3]
        hex_colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i + 1], palette[i + 2]
            hex_colors.append(f"#{r:02X}{g:02X}{b:02X}")
        return hex_colors
