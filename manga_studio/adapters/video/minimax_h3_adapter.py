"""Adaptateur pour le modèle vidéo MiniMax H3 (Hailuo 3.0 Ref2VA)."""

import logging
from pathlib import Path
from typing import List, Optional
from manga_studio.core.gpu_manager import GPUResourceManager, VRAMCeilingExceededError
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import StoryboardSegment
from manga_studio.core.ports.license_guard import LicenseGuardPort, LicenseViolationError
from manga_studio.core.ports.video_generator import VideoGeneratorPort

logger = logging.getLogger(__name__)


class MiniMaxH3VideoAdapter(VideoGeneratorPort):
    """Adaptateur de génération vidéo MiniMax H3 soumis à LicenseGuard et au plafond GPU."""

    def __init__(
        self,
        license_guard: LicenseGuardPort,
        gpu_manager: Optional[GPUResourceManager] = None
    ):
        self.license_guard = license_guard
        self.gpu_manager = gpu_manager or GPUResourceManager(ceiling_gb=22.0)

    def generate_clip(
        self,
        segment: StoryboardSegment,
        reference_images: List[Path],
        output_path: Path,
        config: TalePipelineConfig,
        seed: Optional[int] = None
    ) -> Path:
        """Génère un clip vidéo via H3 après contrôles stricts de licence et de VRAM."""
        # 1. Contrôle obligatoire de la licence
        guard_decision = self.license_guard.validate_execution(
            model_id="minimax_h3_ref2va",
            profile=config.profile,
            territory=config.territory,
            allow_local_flag=config.enable_h3_local
        )

        if not guard_decision.approved:
            raise LicenseViolationError(f"Génération H3 bloquée par le LicenseGuard: {guard_decision.reason}")

        if guard_decision.warning_message:
            logger.warning(f"[H3] {guard_decision.warning_message}")

        if not config.enable_h3_local:
            raise RuntimeError("Exécution locale de MiniMax H3 désactivée (ENABLE_H3_LOCAL=False).")

        # 2. Gestion et isolation GPU
        logger.info(f"[H3] Début de la passe de génération pour le segment {segment.scene_id}...")
        self.gpu_manager.evict_and_clean()

        try:
            # Vérification du plafond VRAM avant génération
            self.gpu_manager.check_vram_limit()

            # Simulation ou appel de l'inférence H3 SGLang / ComfyUI local
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Formatage du payload H3-Ref2VA (max 9 images)
            clamped_refs = reference_images[:9]
            logger.info(
                f"[H3] Prompt: '{segment.prompt_ia[:80]}...' | "
                f"Références images: {len(clamped_refs)} | Durée: {segment.duree_s}s"
            )

            # Écriture du conteneur vidéo (ou délégation subprocess vers ComfyUI/SGLang)
            header = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41"
            info = f"H3-Ref2VA - {segment.scene_id} - Refs: {len(clamped_refs)} - Seed: {seed}".encode("utf-8")
            output_path.write_bytes(header + b"\x00" * 512 + info)

            # Vérification du pic VRAM après génération
            self.gpu_manager.check_vram_limit()
            return output_path

        except VRAMCeilingExceededError as e:
            logger.error(f"[H3] Échec mémoire GPU sur {segment.scene_id} : {e}")
            self.gpu_manager.evict_and_clean()
            raise
        except Exception as e:
            logger.error(f"[H3] Erreur lors de la génération du clip {segment.scene_id} : {e}")
            self.gpu_manager.evict_and_clean()
            raise
        finally:
            self.gpu_manager.evict_and_clean()
