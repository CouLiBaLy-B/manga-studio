"""API Web FastAPI et gestionnaire de médias pour MangaTok Studio."""

import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from manga_studio.core.cover_generator import CoverPosterGenerator
from manga_studio.core.kinetic_subtitles import KineticSubtitleGenerator
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.core.models.storyboard import AudioScriptItem, Storyboard, StoryboardSegment
from manga_studio.core.multiformat_exporter import MultiFormatExporter
from manga_studio.core.prompt_builder import PromptBuilder
from manga_studio.core.social_metadata import SocialMetadataGenerator
from manga_studio.core.style_presets import StylePresetRegistry
from manga_studio.pipeline.runner import AnimatedTalePipelineRunner

app = FastAPI(
    title="MangaTok Studio — Mode « Conte animé » API",
    description="Service de génération vidéo TikTok/Reels avec cohérence visuelle et fiches canoniques",
    version="1.2.0"
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
    style_preset: str = Field(default="watercolor_mythology", description="Clé du preset de style")
    style_suffix: Optional[str] = None


class SegmentUpdateRequest(BaseModel):
    titre: Optional[str] = None
    frame: Optional[str] = None
    prompt_ia: Optional[str] = None
    duree_s: Optional[float] = None
    emotion: Optional[str] = None
    plan: Optional[str] = None
    decor: Optional[str] = None
    audio_dialogues: Optional[List[Dict[str, str]]] = None


class SegmentsReorderRequest(BaseModel):
    scene_ids_in_order: List[str]


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Retourne l'état de santé du studio et des ressources GPU."""
    return {
        "status": "HEALTHY",
        "mode": "Conte animé",
        "version": "1.2.0",
        "gpu_ceiling_gb": 22.0,
        "default_profile": "research",
        "human_in_the_loop_enabled": True,
        "style_presets": [p.model_dump() for p in StylePresetRegistry.list_presets().values()]
    }


@app.get("/api/runs/{story_id}/bible")
def get_character_bible(story_id: str):
    """Retourne la bible canonique verrouillée du run."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    bible_path = run_dir / "character_bible.json"
    if not bible_path.exists():
        raise HTTPException(status_code=404, detail="Bible non trouvée")
    return json.loads(bible_path.read_text(encoding="utf-8"))


@app.get("/api/runs/{story_id}/storyboard")
def get_storyboard(story_id: str):
    """Retourne le storyboard validé du run."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    sb_path = run_dir / "storyboard.validated.json"
    if not sb_path.exists():
        sb_path = run_dir / "storyboard.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard non trouvé")
    return json.loads(sb_path.read_text(encoding="utf-8"))


@app.put("/api/runs/{story_id}/segments/{scene_id}")
def update_segment(story_id: str, scene_id: str, req: SegmentUpdateRequest):
    """Met à jour un segment du storyboard (Human-in-the-Loop)."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    sb_path = run_dir / "storyboard.validated.json"
    if not sb_path.exists():
        sb_path = run_dir / "storyboard.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard introuvable pour ce conte")

    sb_data = json.loads(sb_path.read_text(encoding="utf-8"))
    storyboard = Storyboard.model_validate(sb_data)

    target_seg = None
    for seg in storyboard.segments:
        if seg.scene_id == scene_id:
            target_seg = seg
            break

    if not target_seg:
        raise HTTPException(status_code=404, detail=f"Scène '{scene_id}' introuvable dans le storyboard")

    if req.titre is not None:
        target_seg.titre = req.titre
    if req.frame is not None:
        target_seg.frame = req.frame
    if req.prompt_ia is not None:
        target_seg.prompt_ia = req.prompt_ia
    if req.duree_s is not None:
        target_seg.duree_s = req.duree_s
    if req.emotion is not None:
        target_seg.emotion = req.emotion
    if req.plan is not None:
        target_seg.plan = req.plan
    if req.decor is not None:
        target_seg.decor = req.decor
    if req.audio_dialogues is not None:
        target_seg.audio_script = [
            AudioScriptItem(speaker=d.get("speaker", "Narrateur"), kind="dialogue", text=d.get("text", ""))
            for d in req.audio_dialogues
        ]

    validated_sb = storyboard.model_validate(storyboard.model_dump())
    sb_path.write_text(validated_sb.model_dump_json(indent=2), encoding="utf-8")
    return {"status": "UPDATED", "scene_id": scene_id, "segment": target_seg.model_dump()}


@app.post("/api/runs/{story_id}/reorder")
def reorder_segments(story_id: str, req: SegmentsReorderRequest):
    """Réordonne les segments du storyboard."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    sb_path = run_dir / "storyboard.validated.json"
    if not sb_path.exists():
        sb_path = run_dir / "storyboard.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard introuvable")

    sb_data = json.loads(sb_path.read_text(encoding="utf-8"))
    storyboard = Storyboard.model_validate(sb_data)
    seg_map = {s.scene_id: s for s in storyboard.segments}

    new_segments = []
    for idx, sid in enumerate(req.scene_ids_in_order, start=1):
        if sid in seg_map:
            seg = seg_map[sid]
            seg.ordre = idx
            new_segments.append(seg)

    storyboard.segments = new_segments
    revalidated = storyboard.model_validate(storyboard.model_dump())
    sb_path.write_text(revalidated.model_dump_json(indent=2), encoding="utf-8")
    return {"status": "REORDERED", "total_segments": len(new_segments)}


@app.get("/api/runs/{story_id}/qc")
def get_qc_reports(story_id: str):
    """Retourne l'ensemble des rapports QC du run."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    qc_dir = run_dir / "qc"
    if not qc_dir.exists():
        return []
    reports = []
    for f in sorted(qc_dir.glob("*.json")):
        reports.append(json.loads(f.read_text(encoding="utf-8")))
    return reports


@app.get("/api/runs/{story_id}/manifest")
def get_manifest_events(story_id: str):
    """Retourne le flux des événements de traçabilité."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    manifest_file = run_dir / "manifests" / "render_manifest.jsonl"
    if not manifest_file.exists():
        return []
    events = []
    for line in manifest_file.read_text(encoding="utf-8").strip().split("\n"):
        if line.strip():
            events.append(json.loads(line))
    return events


@app.get("/api/runs/{story_id}/social")
def get_social_metadata(story_id: str):
    """Génère et retourne les métadonnées virales (TikTok, YouTube Shorts, Instagram)."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    sb_path = run_dir / "storyboard.validated.json"
    bible_path = run_dir / "character_bible.json"
    if not sb_path.exists() or not bible_path.exists():
        raise HTTPException(status_code=404, detail="Run non trouvé")

    sb = Storyboard.model_validate(json.loads(sb_path.read_text(encoding="utf-8")))
    bible = CharacterBible.model_validate(json.loads(bible_path.read_text(encoding="utf-8")))
    pkg = SocialMetadataGenerator.generate_package(story_id, sb, bible)
    return pkg.model_dump()


@app.get("/api/media/{story_id}/video")
def get_final_video(story_id: str):
    """Sert la vidéo finale assemblée."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    video_path = run_dir / "conte_final.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Vidéo finale non trouvée")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{story_id}_final.mp4")


@app.get("/api/media/{story_id}/subtitles/{ext}")
def get_subtitles_file(story_id: str, ext: str):
    """Sert les sous-titres SRT ou ASS."""
    run_dir = BASE_DIR / "output" / story_id if (BASE_DIR / "output" / story_id).exists() else DEFAULT_OUTPUT_DIR
    sub_path = run_dir / "subtitles" / f"conte.{ext}"
    if not sub_path.exists():
        raise HTTPException(status_code=404, detail=f"Sous-titre .{ext} introuvable")
    media_type = "text/plain" if ext == "srt" else "text/x-ssa"
    return FileResponse(sub_path, media_type=media_type, filename=f"{story_id}.{ext}")


@app.post("/api/upload-and-run")
async def upload_and_run(
    story_id: str = Form("conte_custom"),
    tale_text: str = Form(...),
    profile: str = Form("research"),
    territory: str = Form("EU"),
    style_preset: str = Form("watercolor_mythology"),
    character_files: List[UploadFile] = File(default=[])
):
    """Endpoint complet d'importation de fichiers et de lancement de génération."""
    output_dir = BASE_DIR / "output" / story_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarde du texte
    story_file = output_dir / "conte.txt"
    story_file.write_text(tale_text, encoding="utf-8")

    # Sauvegarde des images de personnages uploadées
    chars_dir = output_dir / "personnages"
    chars_dir.mkdir(parents=True, exist_ok=True)

    if character_files:
        for idx, f in enumerate(character_files, start=1):
            if f.filename:
                target_file = chars_dir / f.filename
                with target_file.open("wb") as out_f:
                    shutil.copyfileobj(f.file, out_f)
    else:
        # Copie des fixtures par défaut si aucun upload
        fixture_chars = BASE_DIR / "tests" / "fixtures" / "personnages"
        if fixture_chars.exists():
            for p in fixture_chars.glob("*.png"):
                shutil.copy(p, chars_dir / p.name)

    preset_obj = StylePresetRegistry.get_preset(style_preset)
    dep_profile = DeploymentProfile.COMMERCIAL if profile == "commercial" else DeploymentProfile.RESEARCH

    config = TalePipelineConfig(
        story_path=story_file,
        characters_dir=chars_dir,
        output_dir=output_dir,
        profile=dep_profile,
        territory=territory,
        style_preset=style_preset,
        style_suffix=preset_obj.prompt_suffix,
        enable_bedrock=False,
        enable_h3_local=False,
        generate_subtitles=True
    )

    state = AnimatedTalePipelineRunner.run_pipeline(config=config, use_mock_video=True)
    return {
        "status": state.get("status"),
        "story_id": story_id,
        "total_segments": len(state.get("validated_storyboard").segments) if state.get("validated_storyboard") else 0,
        "video_url": f"/api/media/{story_id}/video",
        "subtitles_srt_url": f"/api/media/{story_id}/subtitles/srt",
        "subtitles_ass_url": f"/api/media/{story_id}/subtitles/ass",
        "report_path": str(state.get("run_report_path"))
    }


@app.post("/api/generate")
def trigger_generation(req: TaleRunRequest):
    """Déclenche la génération d'un conte animé (JSON payload)."""
    output_dir = BASE_DIR / "output" / req.story_id
    output_dir.mkdir(parents=True, exist_ok=True)

    story_file = output_dir / "conte.txt"
    story_file.write_text(req.tale_text, encoding="utf-8")

    chars_dir = BASE_DIR / "tests" / "fixtures" / "personnages"
    preset_obj = StylePresetRegistry.get_preset(req.style_preset)
    profile = DeploymentProfile.COMMERCIAL if req.profile == "commercial" else DeploymentProfile.RESEARCH

    config = TalePipelineConfig(
        story_path=story_file,
        characters_dir=chars_dir,
        output_dir=output_dir,
        profile=profile,
        territory=req.territory,
        style_preset=req.style_preset,
        style_suffix=req.style_suffix or preset_obj.prompt_suffix,
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
    """Redirection vers le dashboard Next.js ou vue d'accueil API."""
    return """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0; url=http://localhost:3000/" />
  <title>MangaTok Studio — Mode « Conte animé »</title>
</head>
<body style="background:#090A0F; color:#FFF; font-family:sans-serif; text-align:center; padding:50px;">
  <h1>⚡ MangaTok Studio — Mode « Conte animé »</h1>
  <p>Accédez à l'interface Next.js sur <a href="http://localhost:3000" style="color:#F4C542;">http://localhost:3000</a></p>
  <p><a href="/docs" style="color:#3B82F6;">Documentation Swagger API</a></p>
</body>
</html>"""
