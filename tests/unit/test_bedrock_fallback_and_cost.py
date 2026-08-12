"""Tests unitaires pour l'estimateur de coût Bedrock et le fallback souverain."""

from pathlib import Path
from manga_studio.adapters.character.rule_based_character_extractor import RuleBasedCharacterExtractorAdapter
from manga_studio.adapters.cost.bedrock_cost_estimator_adapter import BedrockCostEstimatorAdapter
from manga_studio.adapters.storyboard.bedrock_glm5_adapter import BedrockGLM5StoryboardAdapter
from manga_studio.adapters.storyboard.local_fallback_adapter import LocalStoryboardFallbackAdapter
from manga_studio.core.models.config import TalePipelineConfig


def test_bedrock_cost_estimator_pricing():
    """Vérifie le calcul conforme aux tarifs officiels ($1.00/1M input, $3.20/1M output)."""
    estimator = BedrockCostEstimatorAdapter()
    extractor = RuleBasedCharacterExtractorAdapter()
    tale_text = "Il était une fois le dieu Râ dans la barque solaire."
    bible = extractor.extract_character_bible("mythe", tale_text, [Path("personnage_01.png")])
    
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        max_run_budget_usd=1.0
    )

    estimate = estimator.estimate_storyboard_cost(tale_text, bible, config)
    assert estimate.estimated_cost_usd > 0.0
    assert estimate.estimated_cost_usd < 0.1  # Doit rester quelques fractions de centime
    assert estimate.is_within_budget is True
    assert estimate.model_id == "zai.glm-5"


def test_bedrock_automatic_fallback_when_disabled():
    """Vérifie que Bedrock bascule de manière transparente sur le fallback local si ENABLE_BEDROCK=False."""
    extractor = RuleBasedCharacterExtractorAdapter()
    tale_text = "Au commencement des temps, Râ régnait sur l'Égypte."
    bible = extractor.extract_character_bible("mythe", tale_text, [Path("personnage_01.png")])
    
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        enable_bedrock=False  # Désactivé par défaut
    )

    fallback_adapter = LocalStoryboardFallbackAdapter()
    bedrock_adapter = BedrockGLM5StoryboardAdapter(fallback_adapter=fallback_adapter)

    storyboard = bedrock_adapter.generate_storyboard("mythe", tale_text, bible, config)
    assert storyboard.schema_version == "1.0"
    assert len(storyboard.segments) >= 1
    assert storyboard.segments[0].scene_id == "scene_001"


def test_bedrock_sovereign_fallback_in_eu_without_remote_transfer():
    """Vérifie le repli local automatique si le territoire est EU et ALLOW_REMOTE_DATA_TRANSFER=False."""
    extractor = RuleBasedCharacterExtractorAdapter()
    tale_text = "Paragraphe 1.\n\nParagraphe 2."
    bible = extractor.extract_character_bible("mythe", tale_text, [Path("personnage_01.png")])
    
    config = TalePipelineConfig(
        story_path=Path("tests/fixtures/conte.txt"),
        characters_dir=Path("tests/fixtures/personnages"),
        territory="EU",
        enable_bedrock=True,
        allow_remote_data_transfer=False  # Interdit le transfert hors UE
    )

    fallback_adapter = LocalStoryboardFallbackAdapter()
    bedrock_adapter = BedrockGLM5StoryboardAdapter(fallback_adapter=fallback_adapter)

    storyboard = bedrock_adapter.generate_storyboard("mythe", tale_text, bible, config)
    assert len(storyboard.segments) == 2
