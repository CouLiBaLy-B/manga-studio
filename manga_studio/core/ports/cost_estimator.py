"""Port pour l'estimation préalable et le plafonnement des coûts d'inférence."""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import TalePipelineConfig


class CostEstimate(BaseModel):
    """Estimation du coût avant invocation du modèle."""
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    budget_cap_usd: float
    is_within_budget: bool
    currency: str = "USD"
    model_id: str


class BudgetExceededError(Exception):
    """Exception levée en cas de dépassement du budget alloué."""
    pass


class CostEstimatorPort(ABC):
    """Interface pour l'estimation de coût d'inférence LLM."""

    @abstractmethod
    def estimate_storyboard_cost(
        self,
        tale_text: str,
        character_bible: CharacterBible,
        config: TalePipelineConfig
    ) -> CostEstimate:
        """Calcule une estimation de coût basée sur la volumétrie prévisionnelle."""
        pass
