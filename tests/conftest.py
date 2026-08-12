"""Fixtures communes : isolation des artefacts produits par l'API."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_api_output_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Chaque test API écrit dans un répertoire temporaire indépendant."""
    import manga_studio.api.app as api_app

    output_root = tmp_path / "output"
    monkeypatch.setattr(api_app, "OUTPUT_ROOT", output_root)
    return output_root
