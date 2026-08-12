"""Moteur de graphe d'états LangGraph pour le pipeline du Conte animé."""

import logging
from typing import Dict
from manga_studio.core.ports.artifact_store import ArtifactStorePort
from manga_studio.pipeline.nodes.assembly_node import AssemblyNode
from manga_studio.pipeline.nodes.character_bible_node import CharacterBibleNode
from manga_studio.pipeline.nodes.clip_generation_node import ClipGenerationNode
from manga_studio.pipeline.nodes.ingestion_node import IngestionNode
from manga_studio.pipeline.nodes.manifest_node import ManifestNode
from manga_studio.pipeline.nodes.quality_control_node import QualityControlNode
from manga_studio.pipeline.nodes.storyboard_node import StoryboardNode
from manga_studio.pipeline.state import TalePipelineState

logger = logging.getLogger(__name__)


class AnimatedTaleStateGraph:
    """Orchestrateur LangGraph / StateGraph séquentiel avec boucle de retry bornée."""

    def __init__(
        self,
        ingestion_node: IngestionNode,
        character_bible_node: CharacterBibleNode,
        storyboard_node: StoryboardNode,
        clip_generation_node: ClipGenerationNode,
        quality_control_node: QualityControlNode,
        assembly_node: AssemblyNode,
        manifest_node: ManifestNode,
        artifact_store: ArtifactStorePort
    ):
        self.ingestion_node = ingestion_node
        self.character_bible_node = character_bible_node
        self.storyboard_node = storyboard_node
        self.clip_generation_node = clip_generation_node
        self.quality_control_node = quality_control_node
        self.assembly_node = assembly_node
        self.manifest_node = manifest_node
        self.artifact_store = artifact_store

    def run(self, initial_state: TalePipelineState) -> TalePipelineState:
        """Exécute les 7 étapes du graphe de bout en bout."""
        state = dict(initial_state)
        config = state["config"]

        # Initialisation du stockage physique
        self.artifact_store.initialize_store(config.output_dir, state.get("story_id", "tale"))

        # Étape 1 : Ingestion
        logger.info("[Pipeline] Exécution de l'étape 1 : Ingestion...")
        state = self.ingestion_node.execute(state)

        # Étape 2 : Fiches Personnages & Bible
        logger.info("[Pipeline] Exécution de l'étape 2 : Fiches Personnages Verrouillées...")
        state = self.character_bible_node.execute(state)

        # Étape 3 : Storyboard LLM
        logger.info("[Pipeline] Exécution de l'étape 3 : Storyboard LLM...")
        state = self.storyboard_node.execute(state)

        # Étape 4 & 5 : Génération & QC avec boucle de retry bornée
        max_retries = config.max_qc_retries
        for cycle in range(max_retries + 1):
            logger.info(f"[Pipeline] Cycle de rendu et contrôle qualité ({cycle + 1}/{max_retries + 1})...")
            state = self.clip_generation_node.execute(state)
            state = self.quality_control_node.execute(state)

            # Vérifier si des clips nécessitent encore un retry
            qc_reports = state.get("qc_reports", {})
            retry_counts = state.get("retry_counts", {})
            pending_retries = [
                cid for cid, r in qc_reports.items()
                if r.status == "failed" and retry_counts.get(cid, 1) <= max_retries
            ]

            if not pending_retries:
                break
            logger.warning(f"[Pipeline] Régénération demandée pour les scènes : {pending_retries}")

        # Étape 6 : Assemblage Vidéo & Audio FFmpeg
        logger.info("[Pipeline] Exécution de l'étape 6 : Assemblage FFmpeg...")
        state = self.assembly_node.execute(state)

        # Étape 7 : Consolidation finale et Manifest
        logger.info("[Pipeline] Exécution de l'étape 7 : Clôture du Manifest et Run Report...")
        state = self.manifest_node.execute(state)

        return state
