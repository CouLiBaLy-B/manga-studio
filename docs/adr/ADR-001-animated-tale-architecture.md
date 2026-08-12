# ADR-001: Hexagonal Architecture and LangGraph Pipeline for Animated Tale Generation

**Statut :** Accepté  
**Date :** 12 août 2026  
**Décideurs :** Principal AI Engineer, AI Research Scientist, MLOps Engineer  
**Contexte :** MangaTok Studio — Mode « Conte animé »

---

## 1. Contexte et Problématique

Le mode « Conte animé » doit orchestrer une chaîne complexe d'opérations d'intelligence artificielle :
- Extraction d'entités et création de fiches personnages canoniques verrouillées à partir d'un conte en français et de 1 à 9 images de référence.
- Génération et validation d'un storyboard structuré via un LLM distant (Amazon Bedrock `zai.glm-5`) ou un Fallback local.
- Sélection déterministe d'images de référence et ordonnancement de clips vidéo.
- Génération séquentielle avec contrôle strict de l'empreinte VRAM GPU (plafond 22 Go).
- Évaluation automatique de la qualité audiovisuelle (similarité DINOv2, attributs CLIP, WER Faster-Whisper) avec politique de retry bornée.
- Assemblage final déterministe FFmpeg avec transitions, normalisation audio EBU R128 (-14 LUFS) et sous-titres SRT/ASS.
- Traçabilité intégrale via un Render Manifest JSONL et un Run Report.

Le système doit être totalement découplé des frameworks tiers (Bedrock, MiniMax H3, FFmpeg, ComfyUI, Diffusers) pour permettre des tests 100% hors-ligne, un remplacement transparent des modèles et une conformité stricte aux licences.

---

## 2. Décision d'Architecture

Nous adoptons une **Architecture Hexagonale (Ports & Adapters)** pilotée par un graphe d'états **LangGraph / Sequential StateGraph**.

### 2.1 Définition des Ports du Domaine

1. `StoryboardLLMPort` : Génère le storyboard JSON validé par Pydantic.
2. `VideoGeneratorPort` : Génère un clip vidéo/audio à partir d'un prompt et de références images.
3. `CharacterSheetExtractorPort` : Extrait et verrouille les fiches personnages canoniques.
4. `ReferenceSelectorPort` : Sélectionne et ordonne les images de référence pour chaque segment.
5. `QualityEvaluatorPort` : Calcule les scores de similarité visuelle (DINOv2/CLIP) et d'intégrité audio.
6. `VideoAssemblerPort` : Concatène ou ré-encode les clips, applique les fondus et normalise l'audio.
7. `ModelRegistryPort` : Gère les métadonnées de modèles, versions et licences.
8. `LicenseGuardPort` : Valide la conformité légale et territoriale avant toute exécution de modèle.
9. `CostEstimatorPort` : Calcule et plafonne les dépenses d'inférence cloud (ex. Bedrock).
10. `ArtifactStorePort` : Stocke et référence de manière immuable tous les artefacts générés.

### 2.2 Implémentation des Adapters

- **Storyboard :** `BedrockGLM5StoryboardAdapter`, `LocalStoryboardFallbackAdapter`.
- **Génération Vidéo :** `MiniMaxH3VideoAdapter` (soumis à validation du LicenseGuard), `MockVideoGeneratorAdapter` (pour tests et profil démo).
- **Contrôle Qualité :** `ClipOrDinoQualityEvaluatorAdapter`, `MockQualityEvaluatorAdapter`.
- **Assemblage :** `FFmpegVideoAssemblerAdapter`.
- **Garde-fous :** `LicenseGuardAdapter`, `BedrockCostEstimatorAdapter`.
- **Stockage :** `LocalArtifactStoreAdapter`.
- **Registre :** `InMemoryModelRegistryAdapter`.

### 2.3 Pipeline LangGraph en 7 Étapes Canoniques

```text
[Input: conte.txt + images]
       │
       ▼
(1. Ingestion & Extraction) ──► (2. Fiches Personnages Verrouillées)
                                              │
                                              ▼
                                    (3. Storyboard LLM)
                                              │
                                              ▼
                                    (4. Génération Clips)
                                              │
                                              ▼
                                    (5. Contrôle Qualité) ◄──► [Boucle Retry ≤ 2]
                                              │
                                              ▼
                                    (6. Assemblage Final FFmpeg)
                                              │
                                              ▼
                                    (7. Manifest & Rapport)
```

---

## 3. Conséquences et Bénéfices

- **Isolation totale des dépendances externes :** Le domaine métier (modèles Pydantic, règles de cohérence, validation d'ordre) n'a aucune dépendance envers AWS SDK ou des bibliothèques de deep learning spécifiques.
- **Testabilité 100% hors-ligne :** Tous les tests unitaires et d'intégration de pipeline s'exécutent sans réseau à l'aide des adaptateurs mockés et de fixtures locales.
- **Résilience opérationnelle :** En cas d'erreur de parsing JSON, une réparation ciblée intervient sans crash du pipeline. En cas d'indisponibilité de Bedrock, le Fallback local prend le relais immédiatement.
- **Observabilité et Traçabilité :** Chaque étape enregistre ses événements dans un fichier `render_manifest.jsonl` horodaté avec hashes SHA-256.
