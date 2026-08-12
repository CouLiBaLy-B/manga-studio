# Protocole de Benchmark & Mesure de Performance GPU

**Projet :** MangaTok Studio — Mode « Conte animé »  
**Date :** 12 août 2026  
**Auteur :** MLOps Engineer & AI Research Scientist

---

## 1. Objectifs de Mesure

Le protocole vise à évaluer de manière empirique et rigoureuse :
1. **Consommation VRAM pic & allocations dynamiques** lors de l'inférence vidéo sur architecture NVIDIA Ampere / Ada Lovelace (RTX 4090 24 Go).
2. **Latence de génération par seconde de vidéo** (Time-to-Second-Generated).
3. **Stabilité thermique et comportement face au plafond strict de 22.0 Go VRAM**.
4. **Précision de l'évaluateur de similarité DINOv2 vs CLIP** sur corpus de test.
5. **Temps d'assemblage et ré-encodage FFmpeg / EBU R128**.

---

## 2. Environnement de Test Cible

- **Hôte OS :** Ubuntu 22.04 LTS / Debian 12 (Linux x86_64)
- **GPU Cible :** NVIDIA GeForce RTX 4090 (24 576 Mo VRAM)
- **Pilote NVIDIA & CUDA :** Driver >= 550.54, CUDA 12.4
- **Runtime Python :** PyTorch 2.4.0+cu124, torchvision, torchaudio
- **Outils de mesure :** `pynvml`, `torch.cuda.max_memory_allocated()`, `ffprobe`

---

## 3. Procédure Expérimentale

### Étape 1 : Baseline Mémoire (Idle & Déchargement)
- Exécuter `torch.cuda.empty_cache()` et `gc.collect()`.
- Mesurer la VRAM de base consommée par le système d'exploitation et le display server.

### Étape 2 : Chargement du Modèle Vidéo
- Charger les poids du modèle (ex: INT8 quantized H3-Base-Ref2VA ou Wan2.1-14B FP8).
- Mesurer `VRAM_loaded = torch.cuda.memory_allocated()`.

### Étape 3 : Inférence Vidéo Séquentielle
- Pour chaque clip (durée 4s, 6s, 10s) :
  1. Enregistrer le timestamp initial $t_0$.
  2. Suivre en continu à 10 Hz la mémoire allouée et réservée.
  3. Mesurer le temps d'inférence $t_1 - t_0$.
  4. Récupérer le pic de mémoire `VRAM_peak = torch.cuda.max_memory_allocated()`.
  5. Vérifier la contrainte : $\text{VRAM}_{\text{peak}} \le 22.0 \text{ Go}$.

### Étape 4 : Évaluation QC & Éviction
- Évincer le modèle vidéo de la VRAM avant de charger les poids DINOv2-ViT-B/14.
- Mesurer la similarité cosinus et le temps d'inférence de l'embedding.

### Étape 5 : Assemblage FFmpeg & Mesures EBU R128
- Exécuter l'assemblage avec filtre `loudnorm` et `xfade`.
- Mesurer la durée d'assemblage totale et le débit d'encodage (FPS).
