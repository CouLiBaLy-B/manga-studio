# C4 Model — Level 3: Component Diagram

**Projet :** MangaTok Studio — Mode « Conte animé »  
**Date :** 12 août 2026

---

## 1. Diagramme des Composants du Domaine et Ports/Adapters

```text
+--------------------------------------------------------------------------------------------------------------------+
|                                                  DOMAIN CORE LAYER                                                 |
|                                                                                                                    |
|  +--------------------------------------------------------------------------------------------------------------+  |
|  | Domain Entities & Value Objects (Pydantic v2)                                                                |  |
|  | - CharacterBible, CharacterSheet, PhysicalDescription, VoiceSuggestion                                      |  |
|  | - Storyboard, StoryboardSegment, SourceRef, AudioScriptItem, TransitionConfig                                |  |
|  | - QCReport, VisualSimilarityResult, AttributeChecks                                                          |  |
|  | - RenderManifest, ManifestEvent, RunReport, ExecutionStats, CostReport                                        |  |
|  +--------------------------------------------------------------------------------------------------------------+  |
|                                                          ^                                                         |
|                                                          | utilise / valide                                        |
|  +-------------------------------------------------------+------------------------------------------------------+  |
|  | Domain Ports (Interfaces Abstraites)                                                                         |  |
|  | - StoryboardLLMPort           - VideoGeneratorPort          - CharacterSheetExtractorPort                    |  |
|  | - ReferenceSelectorPort       - QualityEvaluatorPort        - VideoAssemblerPort                             |  |
|  | - LicenseGuardPort            - CostEstimatorPort           - ArtifactStorePort                              |  |
|  | - ModelRegistryPort                                                                                           |  |
|  +--------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------^---------------------------------------------------------+
                                                           |
                                                           | implémente
+----------------------------------------------------------+---------------------------------------------------------+
|                                                  ADAPTERS LAYER                                                    |
|                                                                                                                    |
|  +-----------------------------------+  +-----------------------------------+  +--------------------------------+  |
|  | Storyboard Adapters               |  | Video Generator Adapters          |  | Quality Evaluator Adapters     |  |
|  | - BedrockGLM5StoryboardAdapter    |  | - MiniMaxH3VideoAdapter           |  | - ClipOrDinoQCEvaluatorAdapter |  |
|  |   (Structured output, AWS SDK)    |  |   (Ref2VA, 9 imgs, prompt built)  |  |   (Cosine similarity & WER)    |  |
|  | - LocalStoryboardFallbackAdapter  |  | - MockVideoGeneratorAdapter       |  | - MockQualityEvaluatorAdapter  |  |
|  |   (Rule-based / Local LLM)        |  |   (Synthetic fixtures, offline)   |  |   (Deterministic test engine)  |  |
|  +-----------------------------------+  +-----------------------------------+  +--------------------------------+  |
|                                                                                                                    |
|  +-----------------------------------+  +-----------------------------------+  +--------------------------------+  |
|  | Video Assembly Adapter            |  | Guard & Policy Adapters           |  | Storage & Registry Adapters    |  |
|  | - FFmpegVideoAssemblerAdapter     |  | - LicenseGuardAdapter             |  | - LocalArtifactStoreAdapter    |  |
|  |   (Concat/Filter, EBU R128, SRT)  |  |   (Commercial/Territory Guard)    |  | - InMemoryModelRegistryAdapter |  |
|  |                                   |  | - BedrockCostEstimatorAdapter     |  |                                |  |
|  +-----------------------------------+  +-----------------------------------+  +--------------------------------+  |
+----------------------------------------------------------^---------------------------------------------------------+
                                                           |
                                                           | orchestre
+----------------------------------------------------------+---------------------------------------------------------+
|                                                 PIPELINE STATE GRAPH                                               |
|                                                                                                                    |
|  +--------------------------------------------------------------------------------------------------------------+  |
|  | LangGraph State Nodes (`manga_studio.pipeline.nodes.*`)                                                        |  |
|  | 1. `IngestionNode` : Lecture du conte, vérification intégrité des 1-9 images, calcul hashes SHA-256.           |  |
|  | 2. `CharacterBibleNode` : Extraction des fiches canoniques et verrouillage immuable (`locked=True`).            |  |
|  | 3. `StoryboardNode` : Génération LLM, validation Pydantic, découpage long conte, réparation JSON ciblée.        |  |
|  | 4. `ClipGenerationNode` : Ordonnancement références, suffixe style, gestion VRAM, génération H3 / Mock.       |  |
|  | 5. `QualityControlNode` : Évaluation DINOv2 / WER, seuils calibrés, boucle de retry (max 2).                   |  |
|  | 6. `AssemblyNode` : Concaténation/Re-encode FFmpeg, fondus, EBU R128 (-14 LUFS), sous-titres SRT/ASS.         |  |
|  | 7. `ManifestNode` : Consolidation finale du `render_manifest.jsonl` et du `run_report.json`.                   |  |
|  +--------------------------------------------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------------------------+
```
