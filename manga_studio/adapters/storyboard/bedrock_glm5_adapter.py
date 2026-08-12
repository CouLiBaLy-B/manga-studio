"""Adaptateur Amazon Bedrock pour la génération de Storyboard avec GLM-5."""

import json
import logging
from typing import Optional
from manga_studio.adapters.storyboard.local_fallback_adapter import LocalStoryboardFallbackAdapter
from manga_studio.core.json_repair import JSONRepairHelper
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.models.storyboard import Storyboard
from manga_studio.core.ports.cost_estimator import CostEstimatorPort
from manga_studio.core.ports.storyboard_llm import StoryboardLLMPort

logger = logging.getLogger(__name__)


class BedrockGLM5StoryboardAdapter(StoryboardLLMPort):
    """Générateur de storyboard via Amazon Bedrock (modèle `zai.glm-5`) avec fallback local."""

    def __init__(
        self,
        cost_estimator: Optional[CostEstimatorPort] = None,
        fallback_adapter: Optional[StoryboardLLMPort] = None
    ):
        self.cost_estimator = cost_estimator
        self.fallback_adapter = fallback_adapter or LocalStoryboardFallbackAdapter()

    def generate_storyboard(
        self,
        story_id: str,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> Storyboard:
        """Génère le storyboard via Bedrock si autorisé et disponible, sinon utilise le fallback."""
        if not config.enable_bedrock:
            logger.info("[Bedrock] Flag ENABLE_BEDROCK=False. Bascule sur LocalStoryboardFallbackAdapter.")
            return self.fallback_adapter.generate_storyboard(story_id, tale_text, character_bible, config)

        # Contrôle du transfert de données transfrontalier
        if config.territory == "EU" and not config.allow_remote_data_transfer:
            logger.warning(
                "[Bedrock] `zai.glm-5` n'est pas vérifié dans la région EU et ALLOW_REMOTE_DATA_TRANSFER=False. "
                "Bascule souveraine sur LocalStoryboardFallbackAdapter."
            )
            return self.fallback_adapter.generate_storyboard(story_id, tale_text, character_bible, config)

        # Contrôle préalable des coûts
        if self.cost_estimator:
            estimate = self.cost_estimator.estimate_storyboard_cost(tale_text, character_bible, config)
            if not estimate.is_within_budget:
                logger.warning(
                    f"[Bedrock] Budget prévisionnel dépassé ({estimate.estimated_cost_usd:.4f}$ > {estimate.budget_cap_usd:.4f}$). "
                    "Bascule sur LocalStoryboardFallbackAdapter."
                )
                return self.fallback_adapter.generate_storyboard(story_id, tale_text, character_bible, config)

        # Tentative d'appel réel Bedrock via boto3
        try:
            import boto3
            bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name="us-east-1" if config.allow_remote_data_transfer else "eu-west-3"
            )

            prompt = self._build_prompt_payload(story_id, tale_text, character_bible, config)
            
            # Appel via Converse API
            response = bedrock.converse(
                modelId="zai.glm-5",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"temperature": 0.2, "maxTokens": 4096}
            )

            raw_text = response["output"]["message"]["content"][0]["text"]
            parsed_json = JSONRepairHelper.extract_and_parse(raw_text)
            return Storyboard.model_validate(parsed_json)

        except Exception as e:
            logger.warning(f"[Bedrock] Échec de l'appel Bedrock ({e}). Bascule de secours sur LocalStoryboardFallbackAdapter.")
            return self.fallback_adapter.generate_storyboard(story_id, tale_text, character_bible, config)

    def _build_prompt_payload(
        self,
        story_id: str,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> str:
        """Construit le prompt textuel strict sans envoyer d'images brutes."""
        bible_json = character_bible.model_dump_json(indent=2)
        return f"""You are a professional animated video storyboard director.
Convert the following French tale into a structured JSON storyboard for vertical video generation (9:16).

CRITICAL CONSTRAINTS:
1. Output ONLY a valid JSON object strictly matching schema version "1.0".
2. Segments order must be strictly increasing: 1, 2, 3...
3. Dialogues in audio_script MUST be in French.
4. prompt_ia MUST be in English and include exact physical attributes from locked character sheets.
5. Do not invent contradictory facts.
6. Append the style suffix: "{config.style_suffix}".

CHARACTER BIBLE:
{bible_json}

TALE TEXT (FRENCH):
{tale_text}

Produce the JSON matching:
{{
  "schema_version": "1.0",
  "story_id": "{story_id}",
  "segments": [...]
}}
"""
