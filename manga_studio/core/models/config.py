"""Modèles de configuration pour le pipeline du Conte animé."""

from enum import Enum
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DeploymentProfile(str, Enum):
    RESEARCH = "research"
    COMMERCIAL = "commercial"


class TalePipelineConfig(BaseModel):
    """Configuration globale du pipeline de conte animé."""
    # Chemins
    story_path: Path = Field(..., description="Chemin vers le fichier conte.txt")
    characters_dir: Path = Field(..., description="Dossier contenant les images de personnages")
    output_dir: Path = Field(default=Path("output"), description="Dossier racine des sorties générées")

    # Profil et Conformité
    profile: DeploymentProfile = Field(default=DeploymentProfile.RESEARCH, description="Profil de déploiement")
    territory: str = Field(default="EU", description="Code territoire ISO (ex: EU, US, UK, FR, JP)")

    # Garde-fous d'activation
    enable_bedrock: bool = Field(default=False, description="Activer l'invocation d'Amazon Bedrock")
    enable_h3_local: bool = Field(default=False, description="Activer l'exécution locale de MiniMax H3")
    allow_model_download: bool = Field(default=False, description="Autoriser le téléchargement de modèles")
    allow_remote_data_transfer: bool = Field(default=False, description="Autoriser le transfert de données hors UE")

    # Budgets et Coûts
    max_monthly_budget_usd: float = Field(default=10.0, ge=0.0, description="Plafond mensuel en dollars")
    max_run_budget_usd: float = Field(default=2.0, ge=0.0, description="Plafond par run en dollars")

    # Contraintes GPU
    vram_ceiling_gb: float = Field(default=22.0, ge=1.0, le=24.0, description="Plafond VRAM maximal en Go")
    gpu_device_id: int = Field(default=0, ge=0, description="Index du GPU CUDA")

    # Paramètres de Génération & Style
    style_preset: str = Field(default="watercolor_mythology", description="Clé du preset stylistique manga")
    style_suffix: str = Field(
        default="epic anime style, consistent character design, cinematic composition, no text artifacts",
        description="Suffixe de prompt invariable pour la cohérence stylistique"
    )
    max_reference_images: int = Field(default=9, ge=1, le=9, description="Nombre maximal d'images de référence par scène")
    seed: Optional[int] = Field(default=42, description="Seed globale pour reproductibilité")

    # Contrôle Qualité (QC)
    qc_similarity_threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Seuil d'acceptation DINOv2")
    qc_review_threshold: float = Field(default=0.68, ge=0.0, le=1.0, description="Seuil de mise en révision")
    max_qc_retries: int = Field(default=2, ge=0, le=3, description="Nombre maximal de régénérations")

    # Assemblage Vidéo & Audio
    target_resolution: Literal["768p", "1080x1920"] = Field(default="1080x1920", description="Résolution finale")
    target_lufs: float = Field(default=-14.0, description="Cible EBU R128 Loudness intégrée en LUFS")
    target_true_peak: float = Field(default=-1.0, description="Pic vrai maximal EBU R128 en dBTP")
    transition_duration_s: float = Field(default=0.3, ge=0.0, le=1.0, description="Durée du fondu de transition")
    generate_subtitles: bool = Field(default=True, description="Générer les sous-titres SRT et ASS")
