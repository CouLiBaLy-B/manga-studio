# ⚡ MangaTok Studio — Mode « Conte animé »

[![CI Pipeline](https://img.shields.io/badge/CI-Passing-brightgreen?style=flat-square&logo=github-actions)](./ci/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue?style=flat-square&logo=python)](pyproject.toml)
[![Architecture](https://img.shields.io/badge/architecture-Hexagonal%20%2F%20LangGraph-orange?style=flat-square)](docs/c4/animated-tale-container.md)
[![VRAM Ceiling](https://img.shields.io/badge/VRAM%20Guard-22.0%20GB%20Ceiling-red?style=flat-square)](benchmarks/benchmark-protocol.md)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Open-lightgrey?style=flat-square)](docs/adr/ADR-002-video-model-license-policy.md)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-success?style=flat-square)](Makefile)

**MangaTok Studio** est un moteur de génération vidéo automatisé pour formats verticaux (TikTok, Reels, Shorts 9:16). Le mode **« Conte animé »** transforme un conte littéraire francophone et un ensemble de 1 à 9 images de personnages en une vidéo verticale cohérente, avec fiches personnages canoniques verrouillées, dialogues français synchronisés, contrôle qualité automatisé (DINOv2/WER), normalisation audio EBU R128 (`-14 LUFS`) et traçabilité intégrale par manifest JSONL.

---

## 📑 Sommaire

1. [Aperçu Fonctionnel & Pipeline en 7 Étapes](#1-aperçu-fonctionnel--pipeline-en-7-étapes)
2. [Architecture Hexagonale & Diagrammes C4](#2-architecture-hexagonale--diagrammes-c4)
3. [Garde-Fous, Souveraineté & Licences](#3-garde-fous-souveraineté--licences)
4. [Démarrage Rapide](#4-démarrage-rapide)
5. [Interface CLI & Exemples](#5-interface-cli--exemples)
6. [Déploiement Docker & Accélération GPU](#6-déploiement-docker--accélération-gpu)
7. [API REST & Dashboard Interactif](#7-api-rest--dashboard-interactif)
8. [Spécifications, ADR & Documentation](#8-spécifications-adr--documentation)
9. [Tests, Benchmarks & Métriques](#9-tests-benchmarks--métriques)

---

## 1. Aperçu Fonctionnel & Pipeline en 7 Étapes

```text
conte.txt + personnages/*.png
        │
        ▼
[1. Ingestion et Vérification Hash SHA-256]
        │
        ▼
[2. Fiches Personnages Canoniques Verrouillées (locked: true)]
        │
        ▼
[3. Storyboard LLM Structuré & Réparable (Amazon Bedrock / Fallback Local)]
        │
        ▼
[4. Génération Séquentielle de Clips (MiniMax H3 / Modular Wan2.1 + TTS)]
        │
        ▼
[5. Contrôle Qualité DINOv2 & WER (Boucle de Retry Bornée <= 2)]
        │
        ▼
[6. Assemblage FFmpeg, Transitions Xfade, EBU R128 (-14 LUFS) & Sous-Titres]
        │
        ▼
[7. Render Manifest JSONL & Run Report Consolidé]
```

### Entrées
- `conte.txt` : Texte littéraire en français (narration, dialogues explicites, actions).
- `personnages/` : 1 à 9 images de référence (`.png`, `.jpg`, `.webp`).

### Sorties Standardisées dans `output/`
- `character_bible.json` : Fiches canoniques invariables avec descriptions physiques, palette hex et voix.
- `storyboard.json` & `storyboard.validated.json` : Storyboard Pydantic v2 chronologique.
- `clips/001.mp4, 002.mp4, ...` : Clips unitaires rendus.
- `qc/001.json, 002.json, ...` : Rapports d'évaluation DINOv2 / WER Faster-Whisper.
- `subtitles/conte.srt` & `conte.ass` : Sous-titres français synchronisés avec timecodes précis.
- `manifests/render_manifest.jsonl` : Journal d'audit pas-à-pas avec horodatage UTC et empreintes SHA-256.
- `manifests/run_report.json` : Rapport exécutif consolidé (statistiques, coûts, licences).
- `conte_final.mp4` : Vidéo verticale 9:16 (1080x1920) normalisée EBU R128.

---

## 2. Architecture Hexagonale & Diagrammes C4

Le système applique rigoureusement le principe de découplage **Ports & Adapters**.

```text
+-----------------------------------------------------------------------------------------------+
|                                          DOMAIN CORE                                          |
|  - Modèles Pydantic : CharacterBible, Storyboard, QCReport, RenderManifest, TalePipelineConfig|
|  - Gestionnaire VRAM GPU : GPUResourceManager (Plafond 22 Go, éviction CUDA)                  |
|  - Utilitaires : PromptBuilder, JSONRepairHelper, SubtitleGenerator, NarrativeChunker         |
+-----------------------------------------------+-----------------------------------------------+
                                                ^
                                                |
        +---------------------------------------+---------------------------------------+
        |                                                                               |
   [Driven Ports]                                                                  [Driving Ports]
- StoryboardLLMPort                                                             - AnimatedTaleStateGraph
- VideoGeneratorPort                                                            - AnimatedTalePipelineRunner
- CharacterSheetExtractorPort                                                   - CLI (`manga_studio.cli`)
- ReferenceSelectorPort                                                         - FastAPI (`manga_studio.api`)
- QualityEvaluatorPort
- VideoAssemblerPort
- LicenseGuardPort
- CostEstimatorPort
- ArtifactStorePort
- ModelRegistryPort
        ^
        |
+-------+---------------------------------------------------------------------------------------+
|                                        ADAPTERS                                               |
| - Storyboard : BedrockGLM5StoryboardAdapter / LocalStoryboardFallbackAdapter                  |
| - Vidéo      : MiniMaxH3VideoAdapter / ModularVideoTTSAdapter / MockVideoGeneratorAdapter     |
| - Audio      : FrenchTTSAdapter (Synthèse vocale française)                                   |
| - QC         : ClipOrDinoQualityEvaluatorAdapter / MockQualityEvaluatorAdapter                |
| - Assemblage : FFmpegVideoAssemblerAdapter (Xfade, Loudnorm -14 LUFS, SRT/ASS)                 |
| - Garde-fous : LicenseGuardAdapter (Territorial/Commercial Guard) / BedrockCostEstimatorAdapter|
| - Stockage   : LocalArtifactStoreAdapter / InMemoryModelRegistryAdapter                      |
+-----------------------------------------------------------------------------------------------+
```

Pour les diagrammes complets C4 :
- [Niveau 1 : Diagramme de Contexte](docs/c4/animated-tale-context.md)
- [Niveau 2 : Diagramme des Conteneurs](docs/c4/animated-tale-container.md)
- [Niveau 3 : Diagramme des Composants](docs/c4/animated-tale-component.md)

---

## 3. Garde-Fous, Souveraineté & Licences

### 🛡️ `LicenseGuard` & MiniMax H3
La **MiniMax H3 Community License Agreement** (2 août 2026) **exclut expressément l'Union Européenne (UE)**, les **USA**, le **UK** et la **Corée du Sud** de son territoire d'exécution open-weights locale.
- **Profil Commercial en UE :** Bloqué automatiquement par `LicenseGuard` (`LicenseViolationError`).
- **Profil Recherche :** Autorisé uniquement avec `DEPLOYMENT_PROFILE=research` et `ENABLE_H3_LOCAL=true`, avec avertissement légal inscrit au manifest.
- **Alternative de Production UE :** `ModularVideoTTSAdapter` combinant diffusion I2V ouverte (Apache 2.0) et TTS français.

### 🔒 Amazon Bedrock & Souveraineté des Données
- Par défaut, la région cible est configurée en UE (`eu-west-3`).
- Si le modèle `zai.glm-5` n'est pas déployé en UE et que `ALLOW_REMOTE_DATA_TRANSFER=false`, le système bascule souverainement et automatiquement sur le `LocalStoryboardFallbackAdapter`.
- **Minimisation :** Aucune image de personnage n'est transmise à Bedrock (seuls le texte et les fiches descriptives sont envoyés).
- **Plafond Budgétaire :** Calcul du coût en amont par `BedrockCostEstimatorAdapter` ($1.00/1M input, $3.20/1M output).

---

## 4. Démarrage Rapide

### Prérequis
- Python 3.11 ou 3.12
- FFmpeg (recommandé pour l'encodage natif)
- GPU NVIDIA avec pilotes CUDA (optionnel, profil CPU/Mock supporté à 100%)

### Installation en 1 minute
```bash
# 1. Cloner le projet
git clone https://github.com/CouLiBaLy-B/manga-studio.git
cd manga-studio

# 2. Installer les dépendances
make dev-install

# 3. Lancer la suite de tests hors-ligne
make test

# 4. Exécuter la démonstration sur le mythe de Râ
make run-demo
```

---

## 5. Interface CLI & Exemples

Le point d'entrée CLI universel permet de piloter tous les paramètres :

```bash
# Exécution standard avec Fallback Local et Mock Video
python3 -m manga_studio.cli.main \
  --story tests/fixtures/conte.txt \
  --characters-dir tests/fixtures/personnages \
  --output-dir demo_output \
  --profile research \
  --territory EU \
  --use-mock-video
```

### Options Principales
| Option | Type | Défaut | Description |
|---|---|---|---|
| `--story` | Path | *Requis* | Chemin vers le fichier conte.txt en français. |
| `--characters-dir` | Path | *Requis* | Dossier contenant les images de personnages (1 à 9). |
| `--output-dir` | Path | `output/` | Répertoire de sortie des artefacts et de la vidéo. |
| `--profile` | `research` \| `commercial` | `research` | Profil d'exécution audité par le LicenseGuard. |
| `--territory` | `EU` \| `US` \| `JP` \| ... | `EU` | Code territoire ISO de déploiement. |
| `--enable-bedrock` | Flag | `False` | Active l'appel LLM Amazon Bedrock `zai.glm-5`. |
| `--enable-h3-local` | Flag | `False` | Active l'inférence locale MiniMax H3 (soumise à VRAM/Guard). |
| `--allow-remote-transfer`| Flag | `False` | Autorise le transfert de texte hors UE. |

---

## 6. Déploiement Docker & Accélération GPU

Le projet propose une pile Docker Compose multi-environnements :

### 1. Démarrer le service applicatif standard (Port 8000)
```bash
# Créez votre configuration locale et remplacez la clé exemple
cp .env.example .env
# Puis démarrez l'API et le dashboard
make docker-up
# ou
docker compose up -d manga-studio-app
```

> **Sécurité :** en Docker, les opérations de génération et d'édition exigent la valeur `MANGA_STUDIO_API_KEY` dans l'en-tête `X-API-Key`. Le dashboard propose un champ de saisie de cette clé, qui n'est pas persistée. Configurez les origines navigateur autorisées avec `MANGA_STUDIO_CORS_ORIGINS`; ne déployez jamais avec un wildcard CORS.

### 2. Démarrer avec accélération NVIDIA CUDA (RTX 4090 / Port 8001)
```bash
docker compose --profile gpu up -d manga-studio-gpu
```

### 3. Orchestration des Modèles Locaux (Modèle Serveur Dédié)
```bash
docker compose -f docker-compose.models.yml up -d
```

---

## 7. API REST & Dashboard Interactif

MangaTok Studio intègre une API FastAPI avec tableau de bord Web moderne :

```bash
# Démarrer le serveur API
make serve
```
Accédez au tableau de bord sur : **`http://localhost:8000`**

### Endpoints Clés
- `GET /api/status` : État de santé, mode actif et plafond VRAM.
- `GET /api/runs/{story_id}/bible` : Consultation de la bible des personnages verrouillée.
- `GET /api/runs/{story_id}/storyboard` : Storyboard validé et timeline des scènes.
- `GET /api/runs/{story_id}/qc` : Rapports d'évaluation DINOv2 / WER.
- `GET /api/runs/{story_id}/manifest` : Flux d'événements du Render Manifest JSONL.
- `POST /api/generate` : Place un nouveau run en file et retourne immédiatement un `job_id` (`202 Accepted`).
- `POST /api/upload-and-run` : Importe les entrées puis place la génération en file (`202 Accepted`).
- `GET /api/jobs/{job_id}` : État durable, progression et résultat d'un job.
- `POST /api/jobs/{job_id}/cancel` : Annule un job encore en attente (clé API requise).

La pile Docker démarre Redis et un worker RQ séparé : le serveur HTTP ne calcule jamais une génération vidéo dans son propre processus. Réglez `MANGA_STUDIO_REDIS_URL`, `MANGA_STUDIO_QUEUE_NAME` et `MANGA_STUDIO_JOB_TIMEOUT_SECONDS` si votre infrastructure Redis est externe.

---

## 8. Spécifications, ADR & Documentation

Tous les artefacts de conception SpecKit sont maintenus dans le dépôt :
- 📋 [Spécification Fonctionnelle](specs/animated-tale-functional-spec.md)
- ⚙️ [Spécification Technique](specs/animated-tale-technical-spec.md)
- 🔍 [Matrice de Traçabilité des Exigences](specs/animated-tale-traceability-matrix.md)
- 🔬 [Évaluation Technologique & Benchmark Scientifique](docs/research/animated-tale-technology-assessment.md)
- 📖 [Registre des Sources & Fact-Checking](docs/research/source-registry.md)
- 🏛️ [ADR-001 : Architecture Hexagonale & LangGraph](docs/adr/ADR-001-animated-tale-architecture.md)
- 🏛️ [ADR-002 : Politique de Licences Modèles Vidéo](docs/adr/ADR-002-video-model-license-policy.md)
- 🏛️ [ADR-003 : Politique Bedrock & Souveraineté](docs/adr/ADR-003-bedrock-data-policy.md)

---

## 9. Tests, Benchmarks & Métriques

### Exécution des Tests
```bash
# Suite complète de tests unitaires et d'intégration
make test-cov
```

### Couverture de Code Mesurée
- **Nombre de tests :** 47 tests (100 % pass rate hors-ligne)
- **Couverture de code :** **90 %** sur l'ensemble des modules (seuil CI fixé à 85 %).
- **Isolation GPU :** Vérification systématique du plafond de 22 Go VRAM et libération de cache CUDA.
