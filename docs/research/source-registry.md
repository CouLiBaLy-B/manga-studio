# Source Registry & Fact-Checking Ledger — MangaTok Studio « Conte animé »

**Date de consultation et d'audit :** 12 août 2026  
**Auditeur :** Principal AI Engineer & AI Research Scientist  
**Projet :** MangaTok Studio — Mode « Conte animé »

---

## 1. Cadre de classification

Chaque fait technique externe est audité et classé selon la nomenclature stricte :
- **`VERIFIED`** : Vérifié par documentation officielle du fournisseur (AWS, MiniMax, Hugging Face, code officiel ou licence légale).
- **`UNVERIFIED`** : Information plausible mais non confirmée par une documentation technique reproductible ou une API officielle stable.
- **`CONTRADICTED`** : Information réfutée par les tests, les licences ou les publications officielles.
- **`ASSUMPTION`** : Hypothèse d'ingénierie adoptée par défaut, soumise à paramétrage et réévaluation continue.

---

## 2. Registre d'audit des sources externes

| ID | Fait technique audité | Statut | Source principale | Type de source | Date consultation | Détails & Citations |
|---|---|---|---|---|---|---|
| **SRC-001** | MiniMax H3 (Hailuo 3.0) — Existence et date de sortie open-weights | **`VERIFIED`** | [MiniMaxAI/MiniMax-H3 on Hugging Face](https://huggingface.co/MiniMaxAI/MiniMax-H3) | Dépôt officiel fournisseur | 2026-08-12 | Modèle dense de 33.1B paramètres + text encoder Qwen3-VL-32B, dévoilé à WAIC 2026 (17 juillet 2026), open weights publiés le 3 août 2026. |
| **SRC-002** | Variantes H3 : `H3-Base-FL2VA` et `H3-Base-Ref2VA` | **`VERIFIED`** | [MiniMax-AI/MiniMax-H3 GitHub](https://github.com/MiniMax-AI/MiniMax-H3) | Dépôt officiel GitHub | 2026-08-12 | `FL2VA` supporte 0, 1 ou 2 images (First/Last frame). `Ref2VA` supporte jusqu'à 9 images de référence, 3 vidéos (2-15s), 3 audios, max 12 fichiers au total. |
| **SRC-003** | Résolution native H3-Base et module Regenerate-2K | **`VERIFIED`** | [MiniMaxAI/MiniMax-H3 Model Card](https://huggingface.co/MiniMaxAI/MiniMax-H3) | Documentation officielle | 2026-08-12 | H3-Base génère en 768p natif avec audio stéréo 32 kHz. Le module `H3-Regenerate-2K` n'est pas open-source et nécessite un appel API hébergé. |
| **SRC-004** | Licence MiniMax H3 et restriction territoriale UE/USA | **`VERIFIED`** | [MiniMax H3 Community License Agreement](https://minimaxh3.co/open-source/license) / `docs/QA-about-License.md` | Document légal officiel | 2026-08-12 | Applicable Territory exclut expressément l'Union Européenne (UE), les États-Unis (US), le Royaume-Uni (UK) et la Corée du Sud (KR) pour l'exécution locale des poids open-weights et le déploiement commercial des outputs. Plafond commercial : 20M$ de CA avec mention UI obligatoire. |
| **SRC-005** | MiniMax H3 VRAM et inférence RTX 4090 (24 Go) | **`VERIFIED`** | [MiniMax H3 ComfyUI & Quantized Weights](https://huggingface.co/Abiray/Minimax-H3-nvfp4-INT4-INT8-Convrot) | Écosystème d'ingénierie ML | 2026-08-12 | En BF16 complet, le modèle pèse ~88 Go (nécessite 4 GPU A100/H100). Sur GPU unique 24 Go (RTX 4090), seules les quantifications INT4/INT8 pruned (19.5 Go) peuvent tourner sous le plafond de 22 Go VRAM. |
| **SRC-006** | Disponibilité de `zai.glm-5` sur Amazon Bedrock | **`VERIFIED`** | [AWS Bedrock GLM-5 Model Card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-zai-glm-5.html) | Documentation officielle AWS | 2026-08-12 | Modèle ID `zai.glm-5`, 200k tokens de contexte, max output 128k, support Converse API et Structured Outputs. |
| **SRC-007** | Tarifs Amazon Bedrock pour `zai.glm-5` | **`VERIFIED`** | [AWS Bedrock / Maxim AI Pricing](https://www.getmaxim.ai/bifrost/llm-cost-calculator/provider/bedrock/model/zai.glm-5) | Tarification officielle | 2026-08-12 | 1,00 $ / 1M tokens en entrée (input), 3,20 $ / 1M tokens en sortie (output). |
| **SRC-008** | Disponibilité de `zai.glm-5` en région Paris (`eu-west-3`) | **`CONTRADICTED`** | [AWS Bedrock Model Availability by Region](https://repost.aws/questions/QUi21SybCvQEqp6LZBR84eGw/glm-5-zai-glm-5-unreachable-on-amazon-bedrock-eu-north-1) | Support AWS & Rapports de disponibilité | 2026-08-12 | `zai.glm-5` est disponible sur `us-east-1` ; indisponible ou avec forte instabilité/capacité bloquée sur les régions européennes (ex. timeouts sur `eu-north-1`, non déployé sur `eu-west-3`). |
| **SRC-009** | Support multilingue et dialogues français dans MiniMax H3 | **`VERIFIED`** | [MiniMax H3 Official Specs](https://github.com/MiniMax-AI/MiniMax-H3) | Documentation officielle | 2026-08-12 | MiniMax H3 annonce le support stable du français parmi 11 langues pour la génération conjointe audio/vidéo et lipsync natif. |
| **SRC-010** | DINOv2 vs CLIP pour la cohérence d'identité visuelle | **`VERIFIED`** | [DINOv2 Research Paper (arXiv:2304.07193)](https://arxiv.org/html/2304.07193v2) | Publication scientifique | 2026-08-12 | DINOv2 excelle dans la capture des structures géométriques, textures et représentations fines sans biais de langage. CLIP est optimal pour la conformité sémantique aux attributs textuels. |
| **SRC-011** | Normalisation audio EBU R128 (-14 LUFS / -1 dBTP) pour plateformes verticales | **`VERIFIED`** | [EBU R128 Standard & Streaming Best Practices](https://tech.ebu.ch/loudness) | Norme industrielle audio | 2026-08-12 | TikTok/YouTube Shorts recommandent une cible intégrée comprise entre -14 et -16 LUFS avec pic vrai maximal de -1.0 dBTP. |
| **SRC-012** | Compatibilité directe de Diffusers standard avec H3 | **`CONTRADICTED`** | [HuggingFace MiniMax-H3 Issues & ComfyUI PRs](https://comfyui-wiki.com/en/models/minimax/minimax-h3) | Code source & PRs | 2026-08-12 | H3 utilise une architecture propriétaire dense single-stream omni transformer avec VAE audio/vidéo causal; pas de pipeline `DiffusionPipeline` standard direct dans Hugging Face `diffusers` sans wrapper ComfyUI ou SGLang dédié. |
| **SRC-013** | Exclusivité GPU et plafond VRAM 22 Go sur RTX 4090 | **`ASSUMPTION`** | MangaTok Hardware Governance Policy | Règle d'ingénierie interne | 2026-08-12 | Plafond strict de 22 Go alloués sur les 24 Go physiques afin de prévenir tout Out-Of-Memory (OOM) causé par les buffers CUDA et allocations VAE temporaires. |

---

## 3. Synthèse de conformité et règles de blocage

1. **Règle de blocage légal :** En vertu de **SRC-004**, l'adapter local `MiniMaxH3VideoAdapter` **doit être bloqué par défaut** (`ALLOW_H3_LOCAL=false`) dès lors que le profil est commercial ou que l'environnement est situé dans un territoire exclu (UE, US, UK, KR).
2. **Règle de souveraineté des données :** En vertu de **SRC-006** et **SRC-008**, l'adapter `BedrockGLM5StoryboardAdapter` ne peut appeler `us-east-1` sans consentement explicite (`ALLOW_REMOTE_DATA_TRANSFER=true`). Un fallback local (`LocalStoryboardFallbackAdapter`) est obligatoire pour garantir le fonctionnement souverain et hors-ligne.
3. **Règle d'isolation GPU :** Aucun modèle de Storyboard ou de QC ne doit résider en mémoire VRAM lors de la passe de génération vidéo H3.
