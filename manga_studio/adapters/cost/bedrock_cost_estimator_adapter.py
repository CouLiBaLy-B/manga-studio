"""Adaptateur d'estimation et de calcul des coûts pour Amazon Bedrock (zai.glm-5)."""

from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig
from manga_studio.core.ports.cost_estimator import CostEstimate, CostEstimatorPort


class BedrockCostEstimatorAdapter(CostEstimatorPort):
    """Calcule le coût prévisionnel selon la grille tarifaire officielle de `zai.glm-5`."""

    INPUT_PRICE_PER_1M = 1.00   # 1.00 USD / 1M tokens
    OUTPUT_PRICE_PER_1M = 3.20  # 3.20 USD / 1M tokens

    def estimate_storyboard_cost(
        self,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> CostEstimate:
        """Estime la consommation en tokens et le coût prévisionnel en dollars."""
        # Heuristique : ~4 caractères par token en moyenne
        prompt_chars = len(tale_text) + len(character_bible.model_dump_json()) + 1000
        estimated_input_tokens = max(100, int(prompt_chars / 3.8))

        # Estimation de la sortie (environ 300 tokens par segment prévisionnel)
        estimated_paragraphs = max(1, tale_text.count("\n\n") + 1)
        estimated_output_tokens = min(4096, max(500, estimated_paragraphs * 350))

        cost_input = (estimated_input_tokens / 1_000_000.0) * self.INPUT_PRICE_PER_1M
        cost_output = (estimated_output_tokens / 1_000_000.0) * self.OUTPUT_PRICE_PER_1M
        total_cost = cost_input + cost_output

        budget_cap = config.max_run_budget_usd
        is_within_budget = total_cost <= budget_cap

        return CostEstimate(
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            estimated_cost_usd=round(total_cost, 6),
            budget_cap_usd=budget_cap,
            is_within_budget=is_within_budget,
            currency="USD",
            model_id="zai.glm-5"
        )
