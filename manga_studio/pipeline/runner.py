"""Exécuteur principal du pipeline du Conte animé."""

from pathlib import Path
from typing import Optional
from manga_studio.adapters import (
    BedrockCostEstimatorAdapter,
    BedrockGLM5StoryboardAdapter,
    ClipOrDinoQualityEvaluatorAdapter,
    FFmpegVideoAssemblerAdapter,
    InMemoryModelRegistryAdapter,
    LicenseGuardAdapter,
    LocalArtifactStoreAdapter,
    LocalStoryboardFallbackAdapter,
    MockQualityEvaluatorAdapter,
    MockVideoGeneratorAdapter,
    ReferenceSelectorAdapter,
    RuleBasedCharacterExtractorAdapter,
)
from manga_studio.core.gpu_manager import GPUResourceManager
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.pipeline.graph import AnimatedTaleStateGraph
from manga_studio.pipeline.nodes.assembly_node import AssemblyNode
from manga_studio.pipeline.nodes.character_bible_node import CharacterBibleNode
from manga_studio.pipeline.nodes.clip_generation_node import ClipGenerationNode
from manga_studio.pipeline.nodes.ingestion_node import IngestionNode
from manga_studio.pipeline.nodes.manifest_node import ManifestNode
from manga_studio.pipeline.nodes.quality_control_node import QualityControlNode
from manga_studio.pipeline.nodes.storyboard_node import StoryboardNode
from manga_studio.pipeline.state import TalePipelineState


class AnimatedTalePipelineRunner:
    """Instancie le graphe et orchestre l'exécution complète d'un conte animé."""

    @classmethod
    def create_default(
        cls,
        config: TalePipelineConfig,
        use_mock_video: bool = True,
        use_mock_qc: bool = False
    ) -> AnimatedTaleStateGraph:
        """Fabrique un graphe configuré avec tous les adaptateurs standards."""
        # 1. Adaptateurs de base
        artifact_store = LocalArtifactStoreAdapter()
        model_registry = InMemoryModelRegistryAdapter()
        license_guard = LicenseGuardAdapter(model_registry=model_registry)
        cost_estimator = BedrockCostEstimatorAdapter()
        gpu_manager = GPUResourceManager(ceiling_gb=config.vram_ceiling_gb, device_id=config.gpu_device_id)

        # 2. Extracteur & Sélecteur
        extractor = RuleBasedCharacterExtractorAdapter()
        ref_selector = ReferenceSelectorAdapter()

        # 3. LLM Storyboard
        fallback_llm = LocalStoryboardFallbackAdapter()
        storyboard_llm = BedrockGLM5StoryboardAdapter(
            cost_estimator=cost_estimator,
            fallback_adapter=fallback_llm
        )

        # 4. Générateur vidéo
        if use_mock_video or not config.enable_h3_local:
            video_generator = MockVideoGeneratorAdapter()
        else:
            from manga_studio.adapters import MiniMaxH3VideoAdapter
            video_generator = MiniMaxH3VideoAdapter(license_guard=license_guard, gpu_manager=gpu_manager)

        # 5. Contrôle qualité
        if use_mock_qc:
            quality_evaluator = MockQualityEvaluatorAdapter()
        else:
            quality_evaluator = ClipOrDinoQualityEvaluatorAdapter()

        # 6. Assemblage
        assembler = FFmpegVideoAssemblerAdapter()

        # 7. Construction des nœuds
        ingestion_node = IngestionNode(artifact_store=artifact_store)
        bible_node = CharacterBibleNode(extractor=extractor, artifact_store=artifact_store)
        storyboard_node = StoryboardNode(storyboard_llm=storyboard_llm, artifact_store=artifact_store)
        clip_gen_node = ClipGenerationNode(
            video_generator=video_generator,
            reference_selector=ref_selector,
            artifact_store=artifact_store,
            gpu_manager=gpu_manager
        )
        qc_node = QualityControlNode(quality_evaluator=quality_evaluator, artifact_store=artifact_store)
        assembly_node = AssemblyNode(video_assembler=assembler, artifact_store=artifact_store)
        manifest_node = ManifestNode(artifact_store=artifact_store, model_registry=model_registry)

        return AnimatedTaleStateGraph(
            ingestion_node=ingestion_node,
            character_bible_node=bible_node,
            storyboard_node=storyboard_node,
            clip_generation_node=clip_gen_node,
            quality_control_node=qc_node,
            assembly_node=assembly_node,
            manifest_node=manifest_node,
            artifact_store=artifact_store
        )

    @classmethod
    def run_pipeline(
        cls,
        config: TalePipelineConfig,
        use_mock_video: bool = True,
        use_mock_qc: bool = False
    ) -> TalePipelineState:
        """Lance l'exécution de bout en bout et retourne l'état final."""
        graph = cls.create_default(config, use_mock_video=use_mock_video, use_mock_qc=use_mock_qc)
        initial_state: TalePipelineState = {
            "config": config,
            "errors": [],
            "status": "RUNNING"
        }
        return graph.run(initial_state)
