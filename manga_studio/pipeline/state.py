"""Définition de l'état immuable du pipeline LangGraph pour le Conte animé."""

from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.manifest import CostReport, ExecutionStats, LicenseAuditRecord
from manga_studio.core.models.qc import QCReport
from manga_studio.core.models.storyboard import Storyboard


class TalePipelineState(TypedDict, total=False):
    """État global partagé entre les nœuds du pipeline."""
    # Entrées
    story_id: str
    tale_text: str
    image_paths: List[Path]
    config: TalePipelineConfig

    # Artefacts intermédiaires
    image_store_map: Dict[str, Path]
    character_bible: CharacterBible
    storyboard: Storyboard
    validated_storyboard: Storyboard
    clip_paths: Dict[str, Path]          # scene_id -> clip_path
    qc_reports: Dict[str, QCReport]      # scene_id -> QCReport
    retry_counts: Dict[str, int]         # scene_id -> attempts made

    # Artefacts finaux
    subtitles_paths: Dict[str, Path]     # "srt" -> path, "ass" -> path
    final_video_path: Optional[Path]
    render_manifest_path: Optional[Path]
    run_report_path: Optional[Path]

    # Suivi & Audit
    stats: ExecutionStats
    costs: CostReport
    license_records: List[LicenseAuditRecord]
    errors: List[str]
    status: str  # "RUNNING", "COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED"
