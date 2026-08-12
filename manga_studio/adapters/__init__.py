"""Exports des adaptateurs de MangaTok Studio."""

from .character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from .character.reference_selector_adapter import ReferenceSelectorAdapter
from .storyboard.bedrock_glm5_adapter import BedrockGLM5StoryboardAdapter
from .storyboard.local_fallback_adapter import LocalStoryboardFallbackAdapter
from .video.minimax_h3_adapter import MiniMaxH3VideoAdapter
from .video.mock_video_adapter import MockVideoGeneratorAdapter
from .video.modular_video_tts_adapter import ModularVideoTTSAdapter
from .audio.french_tts_adapter import FrenchTTSAdapter
from .lipsync.wav2lip_adapter import Wav2LipAdapter
from .lipsync.mock_lipsync_adapter import MockLipSyncAdapter
from .qc.clip_dino_qc_adapter import ClipOrDinoQualityEvaluatorAdapter
from .qc.mock_qc_adapter import MockQualityEvaluatorAdapter
from .assembly.ffmpeg_assembler_adapter import FFmpegVideoAssemblerAdapter
from .guard.license_guard_adapter import LicenseGuardAdapter
from .cost.bedrock_cost_estimator_adapter import BedrockCostEstimatorAdapter
from .storage.local_artifact_store_adapter import LocalArtifactStoreAdapter
from .registry.in_memory_model_registry_adapter import InMemoryModelRegistryAdapter

__all__ = [
    "RuleBasedCharacterExtractorAdapter",
    "ReferenceSelectorAdapter",
    "BedrockGLM5StoryboardAdapter",
    "LocalStoryboardFallbackAdapter",
    "MiniMaxH3VideoAdapter",
    "MockVideoGeneratorAdapter",
    "ModularVideoTTSAdapter",
    "FrenchTTSAdapter",
    "Wav2LipAdapter",
    "MockLipSyncAdapter",
    "ClipOrDinoQualityEvaluatorAdapter",
    "MockQualityEvaluatorAdapter",
    "FFmpegVideoAssemblerAdapter",
    "LicenseGuardAdapter",
    "BedrockCostEstimatorAdapter",
    "LocalArtifactStoreAdapter",
    "InMemoryModelRegistryAdapter",
]
