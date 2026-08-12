"""Interface en ligne de commande (CLI) pour MangaTok Studio - Mode Conte animé."""

import argparse
import logging
import sys
from pathlib import Path
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.pipeline.runner import AnimatedTalePipelineRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("manga_studio.cli")


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur d'arguments CLI."""
    parser = argparse.ArgumentParser(
        description="MangaTok Studio — Mode « Conte animé » : Génération de vidéo verticale à partir d'un conte et d'images."
    )
    parser.add_argument(
        "--story",
        type=Path,
        required=True,
        help="Chemin vers le fichier conte.txt en français."
    )
    parser.add_argument(
        "--characters-dir",
        type=Path,
        required=True,
        help="Dossier contenant les images de personnages (1 à 9)."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Dossier de destination pour les artefacts et la vidéo finale."
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["research", "commercial"],
        default="research",
        help="Profil de déploiement (défaut: research)."
    )
    parser.add_argument(
        "--territory",
        type=str,
        default="EU",
        help="Territoire de déploiement ISO (défaut: EU)."
    )
    parser.add_argument(
        "--enable-bedrock",
        action="store_true",
        default=False,
        help="Activer l'appel réel au LLM Amazon Bedrock."
    )
    parser.add_argument(
        "--enable-h3-local",
        action="store_true",
        default=False,
        help="Activer l'inférence locale MiniMax H3 (soumise à LicenseGuard)."
    )
    parser.add_argument(
        "--allow-remote-transfer",
        action="store_true",
        default=False,
        help="Autoriser le transfert de données hors UE."
    )
    parser.add_argument(
        "--use-mock-video",
        action="store_true",
        default=True,
        help="Utiliser le générateur mock pour un rendu rapide et hors-ligne."
    )
    return parser


def main(args=None) -> int:
    """Point d'entrée principal CLI."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    profile = DeploymentProfile.COMMERCIAL if parsed_args.profile == "commercial" else DeploymentProfile.RESEARCH

    config = TalePipelineConfig(
        story_path=parsed_args.story,
        characters_dir=parsed_args.characters_dir,
        output_dir=parsed_args.output_dir,
        profile=profile,
        territory=parsed_args.territory,
        enable_bedrock=parsed_args.enable_bedrock,
        enable_h3_local=parsed_args.enable_h3_local,
        allow_remote_data_transfer=parsed_args.allow_remote_transfer
    )

    logger.info(f"=== MangaTok Studio — Conte animé ===")
    logger.info(f"Conte : {config.story_path}")
    logger.info(f"Personnages : {config.characters_dir}")
    logger.info(f"Profil : {config.profile.value} | Territoire : {config.territory}")
    logger.info(f"Sortie : {config.output_dir}")

    try:
        final_state = AnimatedTalePipelineRunner.run_pipeline(
            config=config,
            use_mock_video=parsed_args.use_mock_video
        )
        logger.info(f"Pipeline terminé avec le statut : {final_state.get('status')}")
        logger.info(f"Vidéo finale générée : {final_state.get('final_video_path')}")
        logger.info(f"Rapport d'exécution : {final_state.get('run_report_path')}")
        return 0
    except Exception as e:
        logger.error(f"Échec fatal du pipeline : {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
