# C4 Model — Level 2: Container Diagram

**Projet :** MangaTok Studio — Mode « Conte animé »  
**Date :** 12 août 2026

---

## 1. Diagramme des Conteneurs

```text
+--------------------------------------------------------------------------------------------------------------------+
|                                             MANGATOK STUDIO APPLICATION                                            |
|                                                                                                                    |
|  +--------------------------------------------------------------------------------------------------------------+  |
|  | CLI / API Interface (`manga_studio.cli.main`)                                                                |  |
|  | Parse les arguments CLI, charge les configurations d'environnement, initie le StateGraph LangGraph.          |  |
|  +-------------------------------------------------------+------------------------------------------------------+  |
|                                                          |                                                         |
|                                                          v                                                         |
|  +--------------------------------------------------------------------------------------------------------------+  |
|  | Pipeline Orchestrator (`manga_studio.pipeline.graph.AnimatedTaleGraph`)                                       |  |
|  | Coordonne les 7 nœuds d'états immuables, la gestion des erreurs, le fallback et les boucles de retry QC.    |  |
|  +----+-----------------+------------------+------------------+------------------+-------------------+----------+  |
|       |                 |                  |                  |                  |                   |             |
|       v                 v                  v                  v                  v                   v             |
|  +---------+     +---------------+  +---------------+  +--------------+  +---------------+  +-------------------+  |
|  | Node 1  |     | Node 2        |  | Node 3        |  | Node 4       |  | Node 5        |  | Node 6 & 7        |  |
|  | Ingest  | ──► | Fiches Perso  | ─► Storyboard LLM | ─► Gen Clips Vid| ─► QC Auto Eval  | ─► Assemblage FFmpeg|  |
|  | Text/Img|     | Verrouillées  |  | Structuré     |  | Séquentielle |  | DINOv2 / WER  |  | & Manifest JSONL |  |
|  +---------+     +---------------+  +---------------+  +--------------+  +---------------+  +-------------------+  |
|       |                 |                  |                  |                  |                   |             |
|       +-----------------+------------------+------------------+------------------+-------------------+             |
|                                                          |                                                         |
|                                                          v                                                         |
|  +--------------------------------------------------------------------------------------------------------------+  |
|  | Hexagonal Ports & Adapters Layer (`manga_studio.adapters.*`)                                                 |  |
|  | - StoryboardLLM (BedrockGLM5 / LocalFallback)      - VideoGenerator (H3 / MockVideoGenerator)                |  |
|  | - QualityEvaluator (ClipDino / MockQC)             - VideoAssembler (FFmpegAssembler)                         |  |
|  | - LicenseGuard (Territory/Commercial Guard)        - CostEstimator (BedrockPricing)                           |  |
|  | - ArtifactStore (LocalArtifactStore)               - ModelRegistry (InMemoryRegistry)                         |  |
|  +-------------------------------------------------------+------------------------------------------------------+  |
|                                                          |                                                         |
+----------------------------------------------------------+---------------------------------------------------------+
                                                           |
                                                           v
+--------------------------------------------------------------------------------------------------------------------+
|                                           INFRASTRUCTURE & FILE SYSTEM                                             |
|                                                                                                                    |
|  +------------------------------+  +------------------------------+  +------------------------------------------+  |
|  | Local Artifact Store         |  | GPU Resource Manager         |  | FFmpeg / FFprobe Media Processor        |  |
|  | `output/`                    |  | `torch.cuda` VRAM Monitor    |  | - Concat demuxer / Xfade filter          |  |
|  | - character_bible.json       |  | - Hard ceiling: 22 GB        |  | - Loudnorm EBU R128 (-14 LUFS / -1 dBTP) |  |
|  | - storyboard.json            |  | - Explicit model eviction    |  | - Subtitle generator (SRT & ASS)         |  |
|  | - clips/ & qc/ & subtitles/  |  | - Single video worker lock   |  | - Output: 1080x1920 MP4 H.264/AAC        |  |
|  | - render_manifest.jsonl      |  |                              |  |                                          |  |
|  | - run_report.json            |  |                              |  |                                          |  |
|  +------------------------------+  +------------------------------+  +------------------------------------------+  |
+--------------------------------------------------------------------------------------------------------------------+
```
