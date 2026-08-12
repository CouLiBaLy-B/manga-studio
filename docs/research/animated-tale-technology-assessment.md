# Animated Tale Technology Assessment & Scientific Benchmark

**Auteur :** Principal AI Engineer & AI Research Scientist  
**Projet :** MangaTok Studio — Mode « Conte animé »  
**Date :** 12 août 2026  
**Statut :** Validé pour revue d'architecture

---

## 1. Synthèse exécutive

Le mode **« Conte animé »** de MangaTok Studio vise à transformer un conte textuel en français et de 1 à 9 images de personnages en une vidéo verticale cohérente de haute qualité (format TikTok/Reels 9:16).

Cette évaluation technologique analyse rigoureusement les composants de la chaîne de valeur :
1. **Storyboard LLM distant vs local** : Intégration d'Amazon Bedrock (`zai.glm-5`) vs Fallback local structuré.
2. **Générateur vidéo & audio conjointe** : Évaluation de MiniMax H3 (Hailuo 3.0) en mode `Ref2VA` et alternatives ouvertes (Wan2.1, CogVideoX, LTX-Video + TTS français modulaire).
3. **Cohérence visuelle et contrôle qualité (QC)** : Analyse comparative DINOv2 vs CLIP, protocole de calibration de similarité cosinus, WER audio (Faster-Whisper).
4. **Assemblage audiovisuel déterministe** : Traitement FFmpeg, transitions par fondu croisé, normalisation EBU R128 (-14 LUFS / -1 dBTP), et sous-titrage synchrone.

---

## 2. Évaluation de MiniMax H3 (Hailuo 3.0) et alternatives

### 2.1 Spécifications techniques et capacités

| Paramètre | MiniMax H3 (Hailuo 3.0) | Wan2.1 (T2V/I2V 14B) | CogVideoX-5B | Pipeline Vidéo + TTS Découplé | Statut d'évaluation |
|---|---|---|---|---|---|
| **Architecture** | 33.1B dense transformer + Qwen3-VL-32B | 14B Diffusion Transformer (DiT) | 5B DiT | Modèle I2V + Kokoro/ChatTTS/XTTS | `DOCUMENTÉ PAR SOURCE` |
| **Modes d'entrée** | `FL2VA` (0-2 imgs) / `Ref2VA` (≤9 imgs, ≤3 vids, ≤3 audios) | I2V (1 image de départ) | I2V (1 image de départ) | Image + Text prompt + Audio WAV | `DOCUMENTÉ PAR SOURCE` |
| **Génération Audio** | Native conjointe 32 kHz stéréo | Non (vidéo muette) | Non (vidéo muette) | Audio TTS indépendant synchronisé | `DOCUMENTÉ PAR SOURCE` |
| **Résolution native** | 768p (2K via module fermé `Regenerate-2K`) | 720p / 480p | 480p / 720p | 720p / 1080p | `DOCUMENTÉ PAR SOURCE` |
| **Durée par clip** | 4 à 15 secondes (24 fps) | 5 secondes | 6 secondes | 2 à 15 secondes | `DOCUMENTÉ PAR SOURCE` |
| **Support Français** | Listé parmi 11 langues officielles | N/A (vidéo seule) | N/A (vidéo seule) | TTS natif français d'excellence | `DOCUMENTÉ PAR SOURCE` |
| **Poids BF16 complet** | ~88 Go (nécessite 4x GPU 80 Go) | ~28 Go | ~10 Go | ~10 Go + ~1.5 Go (TTS) | `DOCUMENTÉ PAR SOURCE` |
| **Poids Quantifié INT4/INT8** | ~19.5 Go (pruned NVFP4/INT8) | ~14 Go (FP8) | ~6 Go (INT8) | ~6 Go (INT8) + ~1.5 Go | `ESTIMÉ` |
| **Consommation VRAM RTX 4090** | 19.5 à 21.8 Go VRAM (proche limite 22 Go) | 16 à 18 Go VRAM | 11 à 14 Go VRAM | 8 à 12 Go VRAM | `ESTIMÉ` |
| **Licence** | MiniMax H3 Community License (Restric. UE/US/UK/KR) | Apache 2.0 | Apache 2.0 | MIT / Apache 2.0 | `VERIFIED` |

### 2.2 Analyse des risques de MiniMax H3 pour MangaTok Studio

1. **Blocage territorial et légal (Majeur)** : La licence MiniMax H3 exclut explicitement l'UE, les USA, le Royaume-Uni et la Corée du Sud de son "Applicable Territory" pour l'hébergement local des poids open-weights. Pour un déploiement commercial ou européen, l'utilisation locale des poids H3 est **interdite** sauf accord écrit ou passage par l'API SaaS officielle.
2. **Empreinte VRAM critique** : L'exécution locale sur un GPU unique RTX 4090 (24 Go) requiert des poids élagués et quantifiés en INT8/INT4. La marge opérationnelle par rapport au plafond de 22 Go est inférieure à 1 Go, ce qui expose le système à des erreurs OOM si des allocations concurrentes surviennent.
3. **Module 2K propriétaire** : Le passage de 768p à 2K (`H3-Regenerate-2K`) n'est pas open-source et passe par un appel d'infrastructure MiniMax distant.

---

## 3. Évaluation d'Amazon Bedrock et GLM-5 (`zai.glm-5`)

### 3.1 Caractéristiques vérifiées de `zai.glm-5`

- **Date de lancement :** 11 février 2026 (`DOCUMENTÉ PAR SOURCE`).
- **Modèle ID Bedrock :** `zai.glm-5` (`VERIFIED`).
- **Contexte :** 202 752 tokens en entrée, jusqu'à 128 000 tokens en sortie (`DOCUMENTÉ PAR SOURCE`).
- **Tarifs officiels :** 1,00 $ / million tokens en entrée, 3,20 $ / million tokens en sortie (`VERIFIED`).
- **Capacités :** Mode Structured Outputs / JSON strict, support du Tool Calling, raisonnement étendu (`VERIFIED`).

### 3.2 Problématique de souveraineté et disponibilité régionale

- **Régions disponibles :** Principalement déployé sur `us-east-1` (`DOCUMENTÉ PAR SOURCE`).
- **Disponibilité `eu-west-3` (Paris) :** `NON VÉRIFIÉ` / indisponible à la date d'août 2026. Des tests sur `eu-north-1` ont révélé des quotas restreints et des timeouts (`CONTRADICTED` pour un usage fiable immédiat en UE).
- **Règle de conformité MangaTok :**
  - Si `ALLOW_REMOTE_DATA_TRANSFER=false`, Bedrock est désactivé et le pipeline bascule automatiquement vers le `LocalStoryboardFallbackAdapter`.
  - Aucune image de personnage n'est transmise dans les requêtes de storyboard. Seuls les textes du conte et les fiches descriptives textuelles sont envoyés.
  - Plafond de coût configurable avant tout appel via le `CostEstimator`.

---

## 4. Stratégie de cohérence des personnages et métriques QC

### 4.1 Pourquoi DINOv2 surpasse CLIP pour l'identité visuelle

```text
+-------------------+----------------------------------------------------+---------------------------------------------------+
| Critère           | DINOv2 (Vision Transformer auto-supervisé)         | CLIP (Contrastive Language-Image Pretraining)     |
+-------------------+----------------------------------------------------+---------------------------------------------------+
| Objectif          | Préservation des structures géométriques,          | Alignement sémantique image <-> texte.            |
|                   | textures, micro-détails faciaux et vestimentaires. |                                                   |
| Sensibilité pose  | Robuste aux variations de pose et d'éclairage.     | Biais vers le contexte global de la scène.       |
| Risque majeur     | Insensible à la sémantique textuelle abstraite.    | Faux positifs si les couleurs globales matchent.  |
| Rôle dans QC      | Score d'Identité Visuelle (cosine similarity).     | Vérification des attributs (robe or, sceptre).    |
+-------------------+----------------------------------------------------+---------------------------------------------------+
```

### 4.2 Protocole de calibration des seuils de similarité

Pour éviter tout seuil arbitraire :
1. **Constitution du corpus de calibration :**
   - 500 paires positives (même personnage dans des poses, plans et éclairages variés).
   - 500 paires négatives (personnages distincts mais partageant des styles ou des palettes proches).
2. **Mesure de distribution cosinus :**
   - Calcul des distributions $P(\text{score} \mid \text{positive})$ et $P(\text{score} \mid \text{negative})$.
   - Identification du point EER (Equal Error Rate) : typiquement $\tau = 0.72$ pour DINOv2-ViT-B/14.
   - Sélection d'un seuil opérationnel conservateur $\tau_{\text{accept}} = 0.75$ pour minimiser les faux positifs (acceptation à tort d'un personnage incohérent), couplé à une tolérance $\tau_{\text{review}} = 0.65$ pour le marquage `needs_review`.

```text
                 Distribution des scores DINOv2
    Fréquence
       ^
       |        Paires Négatives            Paires Positives
       |          (différents)                   (identiques)
       |           .---.                          .---.
       |          /     \                        /     \
       |         /       \                      /       \
       |        /         \       EER          /         \
       |       /           \       |          /           \
       +------/-------------\------v---------/-------------\---> Score Cosinus
             0.2           0.55   0.72     0.75   0.85    0.95
                                    |        |
                                    |        +-- Seuil Acceptation MangaTok (0.75)
                                    +----------- Seuil Révision (0.68)
```

---

## 5. Spécifications de l'assemblage vidéo (FFmpeg & EBU R128)

1. **Mode d'assemblage adaptatif :**
   - **Fast-path Concat Demuxer :** Utilisé uniquement si tous les clips générés partagent exactement le même fourcc (`h264`), la même résolution (ex: 1080x1920), la même cadence (24 fps constant) et les mêmes paramètres audio (AAC 48kHz stéréo).
   - **Filter Complex avec Xfade / Afade :** Ré-encodage contrôlé lorsque des transitions lissées (fondu de 200 à 300 ms) ou un recadrage/upscale 9:16 sont requis.
2. **Normalisation de la Loudness EBU R128 :**
   - Filtre audio : `-filter:a loudnorm=I=-14:TP=-1.0:LRA=11`.
   - Cible intégrée : `-14 LUFS` (standard TikTok / Reels).
   - True Peak maximum : `-1.0 dBTP` (garantit l'absence de saturation numérique lors du ré-échantillonnage de diffusion).
3. **Élimination des artefacts et pops de transition :**
   - Application d'un micro-fondu audio (`afade=t=in:d=0.01`, `afade=t=out:d=0.01`) ou d'un `acrossfade` de 200 ms pour éliminer toute discontinuité de phase aux jonctions.
4. **Sous-titres synchronisés :**
   - Génération de fichiers SRT et ASS enrichis à partir de la timeline de l'audio script pour affichage stylisé.

---

## 6. Décisions finales d'évaluation

| Composant | Statut Décisionnel | Justification technique et légale |
|---|---|---|
| **MiniMax H3 (Local Open-Weights)** | **`Rejeter`** (pour déploiement de production / commercial UE) <br> **`Adopter avec réserves`** (profil research hors UE uniquement) | La licence communautaire interdit expressément l'utilisation des poids et la distribution des outputs dans l'UE, aux US, au UK et en Corée. Poids BF16 inexploitables sur 24 Go sans forte quantification. Alternative recommandée pour la production : Architecture modulaire I2V + TTS français ou API officielle MiniMax. |
| **Amazon Bedrock (`zai.glm-5`)** | **`Adopter avec réserves`** | Modèle performant et très économique (1$/1M tokens). Toutefois, l'absence de disponibilité confirmée dans `eu-west-3` impose le maintien obligatoire d'un Fallback Local souverain et l'interdiction de transfert de données sensibles hors UE par défaut. |
