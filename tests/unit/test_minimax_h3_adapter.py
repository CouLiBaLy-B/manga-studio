"""Tests unitaires pour l'adaptateur MiniMax H3 (gestion VRAM, exceptions et restrictions)."""

import tempfile
from pathlib import Path
import pytest
from manga_studio.adapters.guard.license_guard_adapter import LicenseGuardAdapter
from manga_studio.adapters.video.minimax_h3_adapter import MiniMaxH3VideoAdapter
from manga_studio.core.gpu_manager import GPUResourceManager, VRAMCeilingExceededError
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.core.models.storyboard import (
    AudioScriptItem,
    SourceRef,
    StoryboardSegment,
    TransitionConfig,
)
from manga_studio.core.ports.license_guard import LicenseViolationError


def create_segment() -> StoryboardSegment:
    return StoryboardSegment(
        ordre=1,
        scene_id="scene_001",
        titre="Scène 1",
        source_refs=[],
        frame="Râ apparaît",
        characters_present=["ra"],
        reference_character_ids=["ra"],
        audio_script=[AudioScriptItem(speaker="Râ", kind="dialogue", text="Texte")],
        prompt_ia="Action prompt. epic anime style",
        duree_s=5.0,
        emotion="épique",
        plan="medium",
        decor="palais",
        continuity_in="",
        continuity_out="",
        transition=TransitionConfig()
    )


def test_h3_adapter_blocked_by_license_guard_in_commercial():
    """Vérifie le blocage immédiat par le guard en profil commercial en UE."""
    guard = LicenseGuardAdapter()
    adapter = MiniMaxH3VideoAdapter(license_guard=guard)

    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        profile=DeploymentProfile.COMMERCIAL,
        territory="EU",
        enable_h3_local=True
    )

    with pytest.raises(LicenseViolationError):
        adapter.generate_clip(create_segment(), [], Path("/tmp/out.mp4"), config)


def test_h3_adapter_blocked_when_local_flag_disabled():
    """Vérifie le blocage lorsque ENABLE_H3_LOCAL=False."""
    guard = LicenseGuardAdapter()
    adapter = MiniMaxH3VideoAdapter(license_guard=guard)

    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        profile=DeploymentProfile.RESEARCH,
        territory="JP",
        enable_h3_local=False
    )

    with pytest.raises(LicenseViolationError):
        adapter.generate_clip(create_segment(), [], Path("/tmp/out.mp4"), config)


def test_h3_adapter_success_in_research_profile():
    """Vérifie l'exécution nominale en profil research hors UE avec flag activé."""
    guard = LicenseGuardAdapter()
    adapter = MiniMaxH3VideoAdapter(license_guard=guard)

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / "001.mp4"
        config = TalePipelineConfig(
            story_path=Path("tests/fixtures/conte.txt"),
            characters_dir=Path("tests/fixtures/personnages"),
            profile=DeploymentProfile.RESEARCH,
            territory="JP",
            enable_h3_local=True
        )

        res = adapter.generate_clip(create_segment(), [Path("tests/fixtures/personnages/personnage_01.png")], out_path, config)
        assert res.exists()
        assert res.stat().st_size > 0
