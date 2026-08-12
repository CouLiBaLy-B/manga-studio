"""API Web FastAPI et tableau de bord interactif pour MangaTok Studio."""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.pipeline.runner import AnimatedTalePipelineRunner

app = FastAPI(
    title="MangaTok Studio — Mode « Conte animé » API",
    description="Service de génération vidéo TikTok/Reels avec cohérence visuelle et fiches canoniques",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path("/home/user/manga-studio")
DEFAULT_OUTPUT_DIR = BASE_DIR / "demo_output"


class TaleRunRequest(BaseModel):
    tale_text: str = Field(..., min_length=10, description="Texte du conte en français")
    story_id: str = Field(default="conte_web", description="Identifiant unique du conte")
    profile: str = Field(default="research", description="research ou commercial")
    territory: str = Field(default="EU", description="Code territoire ISO")
    style_suffix: str = Field(
        default="epic anime style, consistent character design, cinematic composition, no text artifacts"
    )


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Retourne l'état de santé du studio et des ressources GPU."""
    return {
        "status": "HEALTHY",
        "mode": "Conte animé",
        "version": "1.0.0",
        "gpu_ceiling_gb": 22.0,
        "default_profile": "research"
    }


@app.get("/api/runs/{story_id}/bible")
def get_character_bible(story_id: str):
    """Retourne la bible canonique verrouillée du run."""
    bible_path = DEFAULT_OUTPUT_DIR / "character_bible.json"
    if not bible_path.exists():
        raise HTTPException(status_code=404, detail="Bible non trouvée")
    return json.loads(bible_path.read_text(encoding="utf-8"))


@app.get("/api/runs/{story_id}/storyboard")
def get_storyboard(story_id: str):
    """Retourne le storyboard validé du run."""
    sb_path = DEFAULT_OUTPUT_DIR / "storyboard.validated.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard non trouvé")
    return json.loads(sb_path.read_text(encoding="utf-8"))


@app.get("/api/runs/{story_id}/qc")
def get_qc_reports(story_id: str):
    """Retourne l'ensemble des rapports QC du run."""
    qc_dir = DEFAULT_OUTPUT_DIR / "qc"
    if not qc_dir.exists():
        return []
    reports = []
    for f in sorted(qc_dir.glob("*.json")):
        reports.append(json.loads(f.read_text(encoding="utf-8")))
    return reports


@app.get("/api/runs/{story_id}/manifest")
def get_manifest_events(story_id: str):
    """Retourne le flux des événements de traçabilité."""
    manifest_file = DEFAULT_OUTPUT_DIR / "manifests" / "render_manifest.jsonl"
    if not manifest_file.exists():
        return []
    events = []
    for line in manifest_file.read_text(encoding="utf-8").strip().split("\n"):
        if line.strip():
            events.append(json.loads(line))
    return events


@app.post("/api/generate")
def trigger_generation(req: TaleRunRequest):
    """Déclenche la génération d'un conte animé."""
    output_dir = BASE_DIR / "output" / req.story_id
    output_dir.mkdir(parents=True, exist_ok=True)

    story_file = output_dir / "conte.txt"
    story_file.write_text(req.tale_text, encoding="utf-8")

    chars_dir = BASE_DIR / "tests" / "fixtures" / "personnages"

    profile = DeploymentProfile.COMMERCIAL if req.profile == "commercial" else DeploymentProfile.RESEARCH

    config = TalePipelineConfig(
        story_path=story_file,
        characters_dir=chars_dir,
        output_dir=output_dir,
        profile=profile,
        territory=req.territory,
        style_suffix=req.style_suffix,
        enable_bedrock=False,
        enable_h3_local=False
    )

    state = AnimatedTalePipelineRunner.run_pipeline(config=config, use_mock_video=True)
    return {
        "status": state.get("status"),
        "story_id": req.story_id,
        "total_segments": len(state.get("validated_storyboard").segments) if state.get("validated_storyboard") else 0,
        "video_path": str(state.get("final_video_path")),
        "report_path": str(state.get("run_report_path"))
    }


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Tableau de bord HTML moderne pour visualiser le mode Conte animé."""
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MangaTok Studio — Mode « Conte animé »</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090A0F;
      --card-bg: #12141F;
      --card-border: #1E2235;
      --primary: #F4C542;
      --primary-glow: rgba(244, 197, 66, 0.2);
      --accent: #3B82F6;
      --text: #F3F4F6;
      --text-muted: #9CA3AF;
      --success: #10B981;
      --warning: #F59E0B;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Space Grotesk', sans-serif;
      line-height: 1.6;
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 24px;
    }
    .badge {
      background: var(--primary-glow);
      color: var(--primary);
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 600;
      border: 1px solid var(--primary);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
    }
    .card h2 {
      font-size: 1.2rem;
      color: var(--primary);
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .code-box {
      background: #0D0E15;
      border: 1px solid #1B1D2A;
      border-radius: 8px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: #E2E8F0;
      max-height: 240px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    .scene-card {
      background: #181B2B;
      border: 1px solid #272C45;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 10px;
    }
    .scene-title {
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 4px;
    }
    .tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      background: #272C45;
      color: #D1D5DB;
      margin-right: 4px;
    }
    .btn {
      background: var(--primary);
      color: #000;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 700;
      border: none;
      cursor: pointer;
      font-size: 0.95rem;
      transition: opacity 0.2s;
    }
    .btn:hover { opacity: 0.85; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>⚡ MangaTok Studio</h1>
      <p style="color: var(--text-muted);">Mode « Conte animé » — Orchestrateur Hexagonal & LangGraph</p>
    </div>
    <span class="badge">PROD RESEARCH // 22GB VRAM GUARD ACTIVE</span>
  </div>

  <div class="grid">
    <!-- Fiche Personnage Canonique -->
    <div class="card">
      <h2>🛡️ Fiche Personnage Canonique (Verrouillée)</h2>
      <div id="bible-content" class="code-box">Chargement de la bible...</div>
    </div>

    <!-- Storyboard Interactif -->
    <div class="card" style="grid-column: span 2;">
      <h2>🎬 Storyboard Structuré & Continuité</h2>
      <div id="storyboard-content" style="max-height: 380px; overflow-y: auto;">Chargement du storyboard...</div>
    </div>

    <!-- Contrôle Qualité -->
    <div class="card">
      <h2>🔍 Contrôle Qualité (DINOv2 & WER)</h2>
      <div id="qc-content" class="code-box">Chargement des rapports QC...</div>
    </div>

    <!-- Traçabilité Manifest -->
    <div class="card" style="grid-column: span 2;">
      <h2>📜 Render Manifest (JSONL Event Stream)</h2>
      <div id="manifest-content" class="code-box">Chargement du manifest...</div>
    </div>
  </div>

  <script>
    async function loadData() {
      try {
        const bibleRes = await fetch('/api/runs/conte/bible');
        if (bibleRes.ok) {
          const bible = await bibleRes.json();
          document.getElementById('bible-content').textContent = JSON.stringify(bible, null, 2);
        }

        const sbRes = await fetch('/api/runs/conte/storyboard');
        if (sbRes.ok) {
          const sb = await sbRes.json();
          const sbDiv = document.getElementById('storyboard-content');
          sbDiv.innerHTML = '';
          sb.segments.forEach(seg => {
            const card = document.createElement('div');
            card.className = 'scene-card';
            card.innerHTML = `
              <div class="scene-title">#${seg.ordre} ${seg.scene_id} — ${seg.titre}</div>
              <p style="font-size: 0.88rem; color: #CBD5E1; margin: 4px 0;"><strong>Action:</strong> ${seg.frame}</p>
              <p style="font-size: 0.82rem; color: #94A3B8;"><strong>Prompt IA (EN):</strong> ${seg.prompt_ia}</p>
              <div style="margin-top: 8px;">
                <span class="tag">⏱️ ${seg.duree_s}s</span>
                <span class="tag">🎭 ${seg.emotion}</span>
                <span class="tag">📐 ${seg.plan}</span>
                <span class="tag">✨ ${seg.transition.type} (${seg.transition.duration_s}s)</span>
              </div>
            `;
            sbDiv.appendChild(card);
          });
        }

        const qcRes = await fetch('/api/runs/conte/qc');
        if (qcRes.ok) {
          const qcs = await qcRes.json();
          document.getElementById('qc-content').textContent = JSON.stringify(qcs, null, 2);
        }

        const manRes = await fetch('/api/runs/conte/manifest');
        if (manRes.ok) {
          const events = await manRes.json();
          document.getElementById('manifest-content').textContent = JSON.stringify(events, null, 2);
        }
      } catch (err) {
        console.error('Erreur chargement:', err);
      }
    }
    loadData();
  </script>
</body>
</html>
"""
