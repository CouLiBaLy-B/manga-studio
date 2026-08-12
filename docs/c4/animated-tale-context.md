# C4 Model — Level 1: System Context Diagram

**Projet :** MangaTok Studio — Mode « Conte animé »  
**Date :** 12 août 2026

---

## 1. Diagramme de Contexte Système

```text
+---------------------------------------------------------------------------------------------------+
|                                       UTILISATEURS & ACTEURS                                      |
|                                                                                                   |
|  [Créateur de Contenu / Réalisateur Manga]              [Opérateur MLOps / Admin Studio]          |
|  Fournit : conte.txt + 1-9 images personnages           Configure : profils, budgets, GPU, guards |
+------------------------------------+------------------------------------+-------------------------+
                                     |                                    |
                                     | Lance pipeline & consulte vidéo    | Configure & audite
                                     v                                    v
+---------------------------------------------------------------------------------------------------+
|                                   SYSTÈME : MANGATOK STUDIO                                       |
|                                                                                                   |
|  Mode « Conte animé »                                                                             |
|  - Extraction & Fiches personnages canoniques verrouillées                                        |
|  - Génération de Storyboard LLM structuré & réparable                                             |
|  - Ordonnancement & Génération de Clips Vidéo synchronisés                                        |
|  - Contrôle Qualité (QC) automatisé (DINOv2 / CLIP / WER)                                         |
|  - Assemblage FFmpeg déterministe (EBU R128 -14 LUFS, 9:16 vertical, SRT/ASS)                     |
|  - Traçabilité complète (Render Manifest JSONL, Run Report)                                       |
+-------------------+--------------------------------+--------------------------------+-------------+
                    |                                |                                |
                    | Invocation LLM                 | Inférence Vidéo (si autorisé)  | Métriques
                    v                                v                                v
+-------------------------------+  +-------------------------------+  +-------------------------------+
|  AMAZON BEDROCK (zai.glm-5)   |  |   MINIMAX H3 VIDEO CLOUD/API  |  |    LOCALE GPU (RTX 4090)      |
|  (Optionnel / Souveraineté)   |  |   (Optionnel / Soumis Guard)  |  |    - Fallback LLM local       |
|  - Structured JSON Storyboard |  |   - Génération conjointe      |  |    - DINOv2 / CLIP QC Embed   |
|  - Estimations de coûts       |  |   - Audio/Vidéo lipsync FR    |  |    - Faster-Whisper WER FR    |
+-------------------------------+  +-------------------------------+  +-------------------------------+
```

---

## 2. Description des Éléments de Contexte

| Élément | Type | Description & Responsabilités |
|---|---|---|
| **Créateur de Contenu** | Personne | Auteur fournissant le conte en français et les images canoniques des personnages. Visualise la vidéo verticale finale assemblée. |
| **Opérateur MLOps** | Personne | Ingénieur gérant l'infrastructure locale (RTX 4090), les quotas Bedrock, les profils de conformité (`research` vs `commercial`). |
| **MangaTok Studio (Mode Conte Animé)** | Système Logiciel | Moteur central d'orchestration LangGraph réalisant la transformation de bout en bout de l'histoire textuelle en vidéo TikTok/Reels. |
| **Amazon Bedrock** | Système Externe | Fournisseur cloud pour le LLM `zai.glm-5`, soumis au `CostEstimator` et au `BedrockDataPolicy`. |
| **Local GPU (RTX 4090 24 Go)** | Infrastructure | Carte graphique hôte dédiée à l'inférence locale, sous surveillance stricte de VRAM (plafond 22 Go) et politique d'éviction séquentielle. |
