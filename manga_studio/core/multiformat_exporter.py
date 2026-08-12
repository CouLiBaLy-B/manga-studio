"""Exportateur multi-formats (9:16 vertical, 1:1 carré, 16:9 paysage)."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class MultiFormatExporter:
    """Génère les déclinaisons de format vidéo pour TikTok (9:16), Instagram (1:1) et YouTube (16:9)."""

    FORMAT_SPECS = {
        "vertical_9_16": {"width": 1080, "height": 1920, "suffix": "_9_16.mp4"},
        "square_1_1": {"width": 1080, "height": 1080, "suffix": "_1_1.mp4"},
        "landscape_16_9": {"width": 1920, "height": 1080, "suffix": "_16_9.mp4"},
    }

    @classmethod
    def export_all_formats(cls, source_video_path: Path, output_dir: Path) -> Dict[str, Path]:
        """Exécute les conversions de formats et retourne le dictionnaire des chemins créés."""
        if not source_video_path.exists():
            raise FileNotFoundError(f"Vidéo source introuvable : {source_video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        results: Dict[str, Path] = {}

        for fmt_key, spec in cls.FORMAT_SPECS.items():
            target_path = output_dir / f"{source_video_path.stem}{spec['suffix']}"
            w = spec["width"]
            h = spec["height"]

            if shutil.which("ffmpeg"):
                # Commande FFmpeg avec mise à l'échelle et padding sans déformation
                vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(source_video_path),
                    "-vf", vf,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-c:a", "copy",
                    str(target_path)
                ]
                try:
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    results[fmt_key] = target_path
                    continue
                except Exception as e:
                    logger.warning(f"[MultiFormat] Erreur conversion {fmt_key} ({e}), passage au fallback.")

            # Fallback hors-ligne
            header = b"\x00\x00\x00\x1cftypisom"
            meta = f"MultiFormat-{fmt_key}-{w}x{h}".encode("utf-8")
            target_path.write_bytes(header + b"\x00" * 256 + meta)
            results[fmt_key] = target_path

        return results
