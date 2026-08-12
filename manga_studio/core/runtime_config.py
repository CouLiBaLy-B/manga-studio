"""Configuration runtime sûre et portable pour les services MangaTok Studio."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path_from_env(name: str, default: Path) -> Path:
    """Retourne un chemin absolu configurable sans dépendre du poste de développement."""
    return Path(os.getenv(name, str(default))).expanduser().resolve()


DATA_ROOT = _path_from_env("MANGA_STUDIO_DATA_ROOT", PROJECT_ROOT)
OUTPUT_ROOT = _path_from_env("MANGA_STUDIO_OUTPUT_ROOT", DATA_ROOT / "output")
FIXTURES_ROOT = _path_from_env("MANGA_STUDIO_FIXTURES_ROOT", DATA_ROOT / "tests" / "fixtures")
ENVIRONMENT = os.getenv("MANGA_STUDIO_ENV", "development").strip().lower()


def configured_cors_origins() -> list[str]:
    """Lit les origines CORS explicites, sans joker incompatible avec les credentials."""
    raw_origins = os.getenv("MANGA_STUDIO_CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("MANGA_STUDIO_CORS_ORIGINS ne doit pas contenir '*'.")
    return origins
