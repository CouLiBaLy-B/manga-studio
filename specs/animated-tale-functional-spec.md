# Spécification Fonctionnelle — MangaTok Studio : Mode « Conte animé »

**Version :** 1.0.0  
**Statut :** Approuvé  
**Date :** 12 août 2026  
**Auteur :** Principal AI Engineer & Product Architect

---

## 1. Objectif du Produit

Le mode **« Conte animé »** permet aux créateurs de contenu de transformer automatiquement un conte littéraire francophone (mythe, légende, fable, conte traditionnel) et un ensemble d'images de personnages (entre 1 et 9 images) en une vidéo verticale courte et engageante (format TikTok, Reels, YouTube Shorts 9:16) avec narration, dialogues en français, cohérence visuelle stricte des personnages et sous-titres synchronisés.

---

## 2. Entrées Utilisateur

1. **Texte du conte (`conte.txt`)** :
   - Fichier UTF-8 contenant plusieurs paragraphes en français.
   - Contient la narration générale, les descriptions des décors et les dialogues explicites des personnages.
2. **Répertoire d'images de personnages (`personnages/`)** :
   - Contient entre 1 et 9 fichiers images aux formats standards (`.png`, `.jpg`, `.jpeg`, `.webp`).
   - Chaque fichier correspond à un personnage principal ou secondaire de l'histoire.

---

## 3. Sorties Attendues dans `output/`

```text
output/
  ├── character_bible.json       # Fiches personnages canoniques verrouillées
  ├── storyboard.json            # Storyboard brut généré par le LLM
  ├── storyboard.validated.json  # Storyboard revalidé après contrôle de continuité
  ├── clips/                     # Répertoire des clips vidéo générés par segment
  │   ├── 001.mp4
  │   ├── 002.mp4
  │   └── ...
  ├── qc/                        # Rapports individuels de contrôle qualité
  │   ├── 001.json
  │   ├── 002.json
  │   └── ...
  ├── subtitles/                 # Fichiers de sous-titres synchronisés
  │   ├── conte.srt
  │   └── conte.ass
  ├── manifests/                 # Traçabilité et rapports d'audit
  │   ├── render_manifest.jsonl
  │   └── run_report.json
  └── conte_final.mp4            # Vidéo verticale unique assemblée
```

---

## 4. Exigences Fonctionnelles Détaillées

### SF-01 : Ingestion et Extraction Canonique des Personnages
- **SF-01.1 :** Le système extrait les entités de personnages du conte et associe chaque personnage à une image source de manière déterministe.
- **SF-01.2 :** Chaque fiche personnage générée doit être strictement conforme au schéma `CharacterSheet` (silhouette, visage, peau, coiffure, tenue, codes couleurs hexadécimaux, accessoires signature, traits de caractère, voix suggérée en français, contraintes de style).
- **SF-01.3 :** Une fois générée, la fiche est **verrouillée** (`"locked": true`). Aucun nœud ultérieur du pipeline (notamment le storyboard) ne peut altérer l'identité canonique verrouillée.
- **SF-01.4 :** Si un personnage est ambigu ou si une image fournie ne correspond pas au texte, une alerte est enregistrée dans le manifest pour révision humaine.

### SF-02 : Storyboard Structuré et Continuité Narrative
- **SF-02.1 :** Le storyboard est découpé en segments séquentiels chronologiques d'ordre strictement croissant ($1, 2, \dots, N$).
- **SF-02.2 :** Les dialogues doivent être rédigés en **français authentique**, fidèles au texte du conte.
- **SF-02.3 :** Les prompts IA (`prompt_ia`) destinés au générateur vidéo doivent être rédigés en **anglais descriptif**, reprenant rigoureusement les attributs visuels verrouillés de la fiche personnage ainsi que le suffixe de style.
- **SF-02.4 :** Chaque segment doit comporter : `source_refs` (index de paragraphe et citation source), `frame` (description de l'action), `characters_present`, `reference_character_ids`, `audio_script`, `duree_s`, `emotion`, `plan`, `decor`, `continuity_in`, `continuity_out`, et `transition`.
- **SF-02.5 :** Pour les contes longs, le système découpe le conte par blocs narratifs avec mémoire de continuité compacte, puis fusionne et valide l'ensemble.
- **SF-02.6 :** En cas de JSON LLM syntaxiquement invalide, un mécanisme de réparation ciblée intervient avec un maximum de 2 tentatives.

### SF-03 : Génération Visuelle et Cohérence des Personnages
- **SF-03.1 :** Le système sélectionne uniquement les images de référence des personnages actifs dans chaque scène, dans la limite de 9 images.
- **SF-03.2 :** Un suffixe de style constant et versionné (ex: `"epic anime style, consistent character design, no text artifacts"`) est injecté systématiquement dans chaque prompt.
- **SF-03.3 :** La continuité visuelle est assurée par l'injection de `continuity_in` / `continuity_out` et la fixation de seeds déterministes.

### SF-04 : Contrôle Qualité (QC) et Tolérance aux Pannes
- **SF-04.1 :** Chaque clip généré est évalué sur : présence audio, conformité de durée, lisibilité vidéo (ffprobe), score de similarité visuelle (DINOv2 / CLIP) et WER audio (Faster-Whisper).
- **SF-04.2 :** En cas d'échec QC, le clip est régénéré jusqu'à **2 fois maximum** (3 essais au total).
- **SF-04.3 :** Si l'échec persiste après 2 régénérations, le segment est étiqueté `status: "needs_review"` et le pipeline continue son exécution sans planter.

### SF-05 : Assemblage Vidéo Déterministe et Audio EBU R128
- **SF-05.1 :** Concaténation rapide (demuxer) si compatible, ou ré-encodage filtré avec fondu croisé vidéo (200-300 ms).
- **SF-05.2 :** Cadrage vertical 9:16 strict (profil TikTok : 1080x1920, profil démo : 768p).
- **SF-05.3 :** Normalisation sonore EBU R128 (`-14 LUFS`, pic crête vrai `-1 dBTP`).
- **SF-05.4 :** Génération de fichiers de sous-titres synchronisés `.srt` et `.ass`.

### SF-06 : Garde-Fous de Licences et Confidentialité
- **SF-06.1 :** `LicenseGuard` bloque toute exécution commerciale locale de modèles sous licences restrictives (ex. MiniMax H3 en territoire UE/US/UK/KR).
- **SF-06.2 :** Aucune donnée n'est transmise hors de l'UE sans consentement explicite (`ALLOW_REMOTE_DATA_TRANSFER=true`).
- **SF-06.3 :** Plafonnement des coûts Bedrock avec estimation systématique préalable.
