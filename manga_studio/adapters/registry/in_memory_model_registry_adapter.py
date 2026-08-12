"""Adaptateur de registre en mémoire des modèles IA et de leurs licences."""

from typing import Dict, Optional
from manga_studio.core.ports.model_registry import ModelMetadata, ModelRegistryPort


class InMemoryModelRegistryAdapter(ModelRegistryPort):
    """Catalogue de métadonnées de modèles alimenté au démarrage."""

    def __init__(self):
        self._registry: Dict[str, ModelMetadata] = {}
        self._initialize_default_catalog()

    def _initialize_default_catalog(self) -> None:
        """Initialise le catalogue avec les modèles audités."""
        models = [
            ModelMetadata(
                model_id="minimax_h3_ref2va",
                family="MiniMax-H3",
                version="3.0",
                license_name="MiniMax H3 Community License Agreement",
                license_url="https://minimaxh3.co/open-source/license",
                verification_date="2026-08-12",
                status="VERIFIED",
                excluded_territories=["EU", "US", "UK", "KR"],
                commercial_allowed=False,
                vram_requirement_gb=19.5,
                notes="Interdit d'exécution locale et de déploiement en UE/US/UK/KR."
            ),
            ModelMetadata(
                model_id="zai.glm-5",
                family="GLM",
                version="5.0",
                license_name="Amazon Bedrock Commercial API Terms",
                license_url="https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-zai-glm-5.html",
                verification_date="2026-08-12",
                status="VERIFIED",
                excluded_territories=[],
                commercial_allowed=True,
                vram_requirement_gb=0.0,
                notes="Disponible principalement sur us-east-1."
            ),
            ModelMetadata(
                model_id="dinov2_vitb14",
                family="DINOv2",
                version="v2",
                license_name="Apache 2.0",
                license_url="https://github.com/facebookresearch/dinov2",
                verification_date="2026-08-12",
                status="VERIFIED",
                excluded_territories=[],
                commercial_allowed=True,
                vram_requirement_gb=1.8,
                notes="Évaluateur d'identité et de similarité visuelle sans supervision."
            ),
            ModelMetadata(
                model_id="faster_whisper_fr",
                family="Whisper",
                version="large-v3",
                license_name="MIT",
                license_url="https://github.com/SYSTRAN/faster-whisper",
                verification_date="2026-08-12",
                status="VERIFIED",
                excluded_territories=[],
                commercial_allowed=True,
                vram_requirement_gb=2.0,
                notes="Transcription et calcul de WER en français."
            ),
            ModelMetadata(
                model_id="wan_2_1_14b",
                family="Wan",
                version="2.1",
                license_name="Apache 2.0",
                license_url="https://github.com/Wan-Video/Wan2.1",
                verification_date="2026-08-12",
                status="VERIFIED",
                excluded_territories=[],
                commercial_allowed=True,
                vram_requirement_gb=16.5,
                notes="Alternative ouverte recommandée pour génération vidéo."
            )
        ]
        for m in models:
            self.register_model(m)

    def register_model(self, metadata: ModelMetadata) -> None:
        self._registry[metadata.model_id] = metadata

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        return self._registry.get(model_id)

    def list_models(self) -> Dict[str, ModelMetadata]:
        return dict(self._registry)
