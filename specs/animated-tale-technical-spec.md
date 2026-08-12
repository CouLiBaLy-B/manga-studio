# Spécification Technique — MangaTok Studio : Mode « Conte animé »

**Version :** 1.0.0  
**Statut :** Approuvé  
**Date :** 12 août 2026  
**Auteur :** Principal AI Engineer & MLOps Architect

---

## 1. Architecture Logicielle et Contrats d'Interfaces

Le système est structuré selon les principes de l'**Architecture Hexagonale**.

### 1.1 Modèles de Données du Domaine (Pydantic v2)

- **`CharacterSheet`** :
  ```python
  class PhysicalDescription(BaseModel):
      silhouette: str
      visage: str
      peau: str
      coiffure: str
      tenue: str
      couleurs_hex: List[str]
      accessoires_signature: List[str]

  class SuggestedVoice(BaseModel):
      langue: str = "français"
      ton: str

  class CharacterSheet(BaseModel):
      character_id: str
      nom: str
      role: str
      source_image_ids: List[str]
      description_physique: PhysicalDescription
      traits_caractere: List[str]
      voix_suggeree: SuggestedVoice
      style_constraints: List[str]
      locked: bool = True
  ```

- **`Storyboard` & `StoryboardSegment`** :
  ```python
  class SourceRef(BaseModel):
      paragraph_index: int
      excerpt: str

  class AudioScriptItem(BaseModel):
      speaker: str
      kind: Literal["dialogue", "narration", "sound_effect"]
      text: str

  class TransitionConfig(BaseModel):
      type: Literal["fade", "cut", "dissolve", "none"] = "fade"
      duration_s: float = 0.3

  class StoryboardSegment(BaseModel):
      ordre: int
      scene_id: str
      titre: str
      source_refs: List[SourceRef]
      frame: str
      characters_present: List[str]
      reference_character_ids: List[str]
      audio_script: List[AudioScriptItem]
      prompt_ia: str
      duree_s: float
      emotion: str
      plan: str
      decor: str
      continuity_in: str
      continuity_out: str
      transition: TransitionConfig = Field(default_factory=TransitionConfig)
  ```

- **`QCReport`** :
  ```python
  class VisualSimilarityResult(BaseModel):
      model: str = "dinov2"
      score: float
      threshold: float = 0.75

  class QCReport(BaseModel):
      segment_id: str
      attempt: int
      status: Literal["passed", "failed", "needs_review"]
      duration_ok: bool
      audio_present: bool
      dialogue_wer: float
      visual_similarity: VisualSimilarityResult
      attribute_checks: Dict[str, bool]
      issues: List[str]
      recommendation: Literal["accept", "retry", "flag_review"]
  ```

---

## 2. Ports du Domaine

```python
class StoryboardLLMPort(ABC):
    @abstractmethod
    def generate_storyboard(self, tale_text: str, bible: CharacterBible, config: StoryboardConfig) -> Storyboard:
        pass

class VideoGeneratorPort(ABC):
    @abstractmethod
    def generate_clip(self, segment: StoryboardSegment, ref_images: List[Path], output_path: Path, seed: Optional[int] = None) -> Path:
        pass

class QualityEvaluatorPort(ABC):
    @abstractmethod
    def evaluate_clip(self, clip_path: Path, segment: StoryboardSegment, ref_images: List[Path], attempt: int) -> QCReport:
        pass

class VideoAssemblerPort(ABC):
    @abstractmethod
    def assemble_video(self, clip_paths: List[Path], segments: List[StoryboardSegment], output_path: Path, config: AssemblyConfig) -> Path:
        pass

class LicenseGuardPort(ABC):
    @abstractmethod
    def validate_execution(self, model_id: str, profile: DeploymentProfile, territory: str) -> GuardDecision:
        pass

class CostEstimatorPort(ABC):
    @abstractmethod
    def estimate_storyboard_cost(self, tale_text: str, bible: CharacterBible) -> CostEstimate:
        pass
```

---

## 3. Gestion Mémoire GPU et Plafond VRAM (RTX 4090 - 22 Go)

1. **Isolation stricte de la passe de rendu vidéo :**
   - Avant invocation du générateur vidéo (H3 / local), appel explicite à `torch.cuda.empty_cache()` et `gc.collect()`.
   - Vérification de la VRAM disponible via `torch.cuda.mem_get_info()`.
2. **Plafond VRAM :**
   - Plafond maximal autorisé : `22.0 Go` (23 622 320 128 octets).
   - Si l'allocation VRAM mesurée dépasse 22 Go ou si un avertissement mémoire survient, le job s'arrête proprement, libère les allocations résiduelles et enregistre un diagnostic dans le manifest.

---

## 4. Pipeline d'Assemblage FFmpeg Déterministe

- **Normalisation Audio :**
  `ffmpeg -i input.mp4 -af "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=summary" -c:v copy output.mp4`
- **Transitions Vidéo (Xfade) :**
  Génération dynamique du filtre `[0:v][1:v]xfade=transition=fade:duration=0.3:offset={offset}[v1]` avec ajustement de l'audio `acrossfade=d=0.3`.
- **Génération Sous-Titres (SRT/ASS) :**
  Calcul des timecodes cumulés à partir de la durée de chaque segment et synchronisation des répliques françaises.
