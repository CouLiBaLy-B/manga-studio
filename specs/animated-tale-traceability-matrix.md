# Matrice de Traçabilité des Exigences — MangaTok Studio « Conte animé »

**Date :** 12 août 2026  
**Statut :** Validé

---

| Exigence Fonctionnelle | Exigence Technique | Composant / Port / Adapter | Tests Unitaires & Intégration | Statut |
|---|---|---|---|---|
| **SF-01.1** Ingestion conte & 1-9 images | ST-01 Ingestion déterministe & hash SHA-256 | `IngestionNode`, `ArtifactStorePort`, `LocalArtifactStoreAdapter` | `test_ingestion_node.py`, `test_artifact_store.py` | Validé |
| **SF-01.2 / SF-01.3** Fiches personnages canoniques verrouillées | ST-02 Modèle Pydantic `CharacterSheet` & `locked=True` | `CharacterSheetExtractorPort`, `RuleBasedCharacterExtractorAdapter` | `test_character_sheet_locking.py`, `test_character_extractor.py` | Validé |
| **SF-02.1 / SF-02.4** Storyboard structuré & validation Pydantic | ST-03 Schéma Pydantic `Storyboard` & validation d'ordre | `StoryboardLLMPort`, `StoryboardSegment`, `Storyboard` | `test_storyboard_pydantic_validation.py`, `test_storyboard_ordering.py` | Validé |
| **SF-02.5** Chunking narratif & continuité contes longs | ST-04 Découpage & fusion avec mémoire de continuité | `StoryboardNode`, `LocalStoryboardFallbackAdapter` | `test_narrative_continuity_and_chunking.py` | Validé |
| **SF-02.6** Réparation ciblée JSON LLM | ST-05 Algorithme de correction syntaxique JSON | `JSONRepairHelper`, `BedrockGLM5StoryboardAdapter` | `test_json_repair.py` | Validé |
| **SF-03.1** Sélection des références actives (≤9) | ST-06 Port `ReferenceSelectorPort` | `ReferenceSelectorAdapter` | `test_reference_selector.py` | Validé |
| **SF-03.2 / SF-03.3** Cohérence visuelle & style suffix | ST-07 Injection suffixe & seeds déterministes | `PromptBuilder`, `ClipGenerationNode` | `test_prompt_builder_and_style_suffix.py` | Validé |
| **SF-04.1** Contrôle qualité (DINOv2, CLIP, WER) | ST-08 Port `QualityEvaluatorPort` & `QCReport` | `ClipOrDinoQualityEvaluatorAdapter`, `MockQualityEvaluatorAdapter` | `test_quality_evaluator.py`, `test_qc_threshold_calibration.py` | Validé |
| **SF-04.2 / SF-04.3** Boucle de retry bornée (≤2) | ST-09 Algorithme de retry et flag `needs_review` | `QualityControlNode`, `AnimatedTaleGraph` | `test_bounded_regeneration_policy.py` | Validé |
| **SF-05.1 / SF-05.2** Assemblage FFmpeg 9:16 & transitions | ST-10 Concat demuxer / Xfade filter builder | `VideoAssemblerPort`, `FFmpegVideoAssemblerAdapter` | `test_ffmpeg_assembler.py`, `test_ffmpeg_command_builder.py` | Validé |
| **SF-05.3** Normalisation loudness EBU R128 (-14 LUFS) | ST-11 Filtre FFmpeg `loudnorm` (-14 LUFS / -1 dBTP) | `FFmpegVideoAssemblerAdapter` | `test_ebur128_loudness_normalization.py` | Validé |
| **SF-05.4** Sous-titres synchronisés (SRT / ASS) | ST-12 Générateur de timeline de sous-titres | `SubtitleGenerator`, `FFmpegVideoAssemblerAdapter` | `test_subtitle_generator.py` | Validé |
| **SF-06.1** LicenseGuard & blocage commercial H3 | ST-13 Port `LicenseGuardPort` & règles territoriales | `LicenseGuardAdapter` | `test_license_guard.py` | Validé |
| **SF-06.2 / SF-06.3** Bedrock Data Policy & Plafond Coûts | ST-14 Port `CostEstimatorPort` & Fallback local | `BedrockCostEstimatorAdapter`, `LocalStoryboardFallbackAdapter` | `test_bedrock_fallback_and_cost.py` | Validé |
| **ST-GPU** Plafond VRAM 22 Go & nettoyage CUDA | ST-15 Gestionnaire mémoire & logs VRAM | `GPUResourceManager` | `test_gpu_vram_manager.py` | Validé |
| **ST-MAN** Render Manifest JSONL & Run Report | ST-16 Journalisation immuable d'événements | `ManifestNode`, `RenderManifest` | `test_render_manifest_generation.py` | Validé |
| **E2E** Pipeline bout-en-bout conte français (Râ) | ST-17 Exécution complète sur conte fixture | `AnimatedTalePipelineRunner` | `test_e2e_animated_tale_pipeline.py` | Validé |
