"""Modèles de domaine pour le Contrôle Qualité (QC) des clips générés."""

from typing import Dict, List, Literal
from pydantic import BaseModel, Field


class VisualSimilarityResult(BaseModel):
    """Résultat de similarité visuelle basé sur DINOv2 ou CLIP."""
    model: str = Field(default="dinov2", description="Nom du modèle de vision utilisé")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de similarité cosinus mesuré")
    threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Seuil d'acceptation minimal calibré")


class QCReport(BaseModel):
    """Rapport de contrôle qualité unitaire pour un clip généré."""
    segment_id: str = Field(..., description="Identifiant du segment analysé (ex: scene_001)")
    attempt: int = Field(default=1, ge=1, le=3, description="Numéro de la tentative (1, 2 ou 3)")
    status: Literal["passed", "failed", "needs_review"] = Field(..., description="Statut global QC")
    duration_ok: bool = Field(default=True, description="La durée réelle correspond à la tolérance")
    audio_present: bool = Field(default=True, description="Piste audio présente et non silencieuse")
    dialogue_wer: float = Field(default=0.0, ge=0.0, le=1.0, description="Word Error Rate mesuré par Faster-Whisper")
    visual_similarity: VisualSimilarityResult = Field(..., description="Mesure de cohérence visuelle")
    attribute_checks: Dict[str, bool] = Field(default_factory=dict, description="Vérification des attributs clés (ex: gold_robes)")
    issues: List[str] = Field(default_factory=list, description="Liste des anomalies détectées")
    recommendation: Literal["accept", "retry", "flag_review"] = Field(..., description="Recommandation de l'évaluateur")
