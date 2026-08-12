"""Tests unitaires pour l'utilitaire de réparation ciblée JSON LLM."""

import pytest
from manga_studio.core.json_repair import JSONRepairHelper


def test_json_repair_clean_json():
    """Vérifie le parsing direct d'un JSON valide."""
    raw = '{"schema_version": "1.0", "story_id": "test"}'
    parsed = JSONRepairHelper.extract_and_parse(raw)
    assert parsed["schema_version"] == "1.0"
    assert parsed["story_id"] == "test"


def test_json_repair_markdown_fences():
    """Vérifie l'extraction du JSON encadré par des backticks markdown."""
    raw = """
    Here is the requested storyboard:
    ```json
    {
      "schema_version": "1.0",
      "story_id": "ra_myth"
    }
    ```
    I hope this helps!
    """
    parsed = JSONRepairHelper.extract_and_parse(raw)
    assert parsed["schema_version"] == "1.0"
    assert parsed["story_id"] == "ra_myth"


def test_json_repair_trailing_commas():
    """Vérifie la correction des virgules traînantes."""
    raw = """
    {
      "story_id": "tale_01",
      "segments": [
        {"ordre": 1, "scene_id": "scene_001",},
      ],
    }
    """
    parsed = JSONRepairHelper.extract_and_parse(raw)
    assert parsed["story_id"] == "tale_01"
    assert len(parsed["segments"]) == 1


def test_json_repair_unbalanced_braces():
    """Vérifie la fermeture automatique des accolades tronquées."""
    raw = '{"story_id": "tale_truncated", "segments": [{"scene_id": "scene_001"'
    parsed = JSONRepairHelper.extract_and_parse(raw)
    assert parsed["story_id"] == "tale_truncated"
    assert parsed["segments"][0]["scene_id"] == "scene_001"
