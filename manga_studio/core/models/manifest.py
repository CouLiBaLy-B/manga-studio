"""Modèles de domaine pour le Manifest d'exécution et le Rapport de run."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ManifestEvent(BaseModel):
    """Événement unitaire enregistré dans render_manifest.jsonl."""
    event_id: str = Field(..., description="UUID ou identifiant unique de l'événement")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO 8601 UTC"
    )
    step: str = Field(..., description="Étape du pipeline (ingestion, bible, storyboard, clip_gen, qc, assembly, finalize)")
    action: str = Field(..., description="Action spécifique effectuée")
    status: str = Field(..., description="Résultat: SUCCESS, WARNING, FAILED, RETRY, SKIPPED")
    details: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées, hashes, paramètres")
    error: Optional[str] = Field(default=None, description="Message d'erreur éventuel")


class CostReport(BaseModel):
    """Rapport financier et volumétrie de tokens."""
    provider: str = Field(default="amazon-bedrock", description="Fournisseur LLM")
    model_id: str = Field(default="zai.glm-5", description="Identifiant du modèle")
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    budget_cap_usd: float = Field(default=5.0, ge=0.0)
    budget_exceeded: bool = Field(default=False)


class ExecutionStats(BaseModel):
    """Statistiques d'exécution de la génération."""
    total_segments: int = Field(default=0)
    total_clips_generated: int = Field(default=0)
    total_regenerations: int = Field(default=0)
    qc_passed_count: int = Field(default=0)
    qc_needs_review_count: int = Field(default=0)
    total_video_duration_s: float = Field(default=0.0)
    pipeline_execution_time_s: float = Field(default=0.0)


class LicenseAuditRecord(BaseModel):
    """Enregistrement d'audit de conformité des licences."""
    component: str = Field(..., description="Composant audité (ex: video_generator, storyboard_llm)")
    model_id: str = Field(..., description="Nom du modèle")
    license_name: str = Field(..., description="Nom officiel de la licence")
    territory: str = Field(..., description="Territoire d'exécution configuré")
    profile: str = Field(..., description="Profil de déploiement (research / commercial)")
    decision: str = Field(..., description="APPROVED / BLOCKED / WARNING")
    reason: str = Field(..., description="Justification légale")


class RunReport(BaseModel):
    """Rapport global consolidé de fin d'exécution (`run_report.json`)."""
    run_id: str = Field(..., description="Identifiant unique du run")
    story_id: str = Field(..., description="Identifiant du conte")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(..., description="COMPLETED, COMPLETED_WITH_WARNINGS, FAILED")
    stats: ExecutionStats = Field(default_factory=ExecutionStats)
    costs: CostReport = Field(default_factory=CostReport)
    licenses: List[LicenseAuditRecord] = Field(default_factory=list)
    output_video_path: Optional[str] = Field(default=None)
    subtitles_paths: Dict[str, str] = Field(default_factory=dict)
    summary: str = Field(default="")
