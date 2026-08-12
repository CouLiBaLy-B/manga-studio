"""API Web FastAPI et gestionnaire de médias pour MangaTok Studio."""

import hmac
import json
from io import BytesIO
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field
from manga_studio.core.cover_generator import CoverPosterGenerator
from manga_studio.core.kinetic_subtitles import KineticSubtitleGenerator
from manga_studio.core.models.character import CharacterBible
from manga_studio.core.models.config import DeploymentProfile
from manga_studio.core.models.storyboard import AudioScriptItem, Storyboard, StoryboardSegment
from manga_studio.core.multiformat_exporter import MultiFormatExporter
from manga_studio.core.prompt_builder import PromptBuilder
from manga_studio.core.social_metadata import SocialMetadataGenerator
from manga_studio.core.style_presets import StylePresetRegistry
from manga_studio.core.runtime_config import (
    ENVIRONMENT,
    FIXTURES_ROOT,
    OUTPUT_ROOT,
    configured_cors_origins,
)
from manga_studio.jobs import cancel_job, enqueue_generation, get_job, job_response

app = FastAPI(
    title="MangaTok Studio — Mode « Conte animé » API",
    description="Service de génération vidéo TikTok/Reels avec cohérence visuelle et fiches canoniques",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "X-API-Key"],
)

STORY_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_IMAGE_MEDIA_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_SUBTITLE_EXTENSIONS = {"srt", "ass"}
MAX_CHARACTER_FILES = 9
MAX_UPLOAD_BYTES = int(os.getenv("MANGA_STUDIO_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_TALE_CHARACTERS = int(os.getenv("MANGA_STUDIO_MAX_TALE_CHARACTERS", "100000"))


def _validated_story_id(story_id: str) -> str:
    """Valide un identifiant de run avant toute construction de chemin."""
    if not STORY_ID_PATTERN.fullmatch(story_id):
        raise HTTPException(
            status_code=422,
            detail="story_id invalide : utilisez 1 à 64 caractères alphanumériques, '-' ou '_'.",
        )
    return story_id


def _run_dir(story_id: str) -> Path:
    """Construit un répertoire de run garanti contenu dans OUTPUT_ROOT."""
    safe_story_id = _validated_story_id(story_id)
    root = OUTPUT_ROOT.resolve()
    run_dir = (root / safe_story_id).resolve()
    if not run_dir.is_relative_to(root):  # Défense en profondeur malgré la whitelist.
        raise HTTPException(status_code=422, detail="Répertoire de run invalide.")
    return run_dir


def _existing_run_dir(story_id: str) -> Path:
    run_dir = _run_dir(story_id)
    if not run_dir.is_dir():
        raise HTTPException(status_code=404, detail="Run non trouvé")
    return run_dir


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Protège les opérations mutables par une clé fournie via X-API-Key.

    En production, l'absence de clé configurée bloque le service plutôt que de
    l'exposer accidentellement. Le mode development explicite conserve la
    simplicité de l'exécution locale.
    """
    expected_key = os.getenv("MANGA_STUDIO_API_KEY")
    if not expected_key:
        if ENVIRONMENT == "production":
            raise HTTPException(status_code=503, detail="Clé API de production non configurée.")
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected_key):
        raise HTTPException(status_code=401, detail="Clé API invalide ou absente.")


class TaleRunRequest(BaseModel):
    tale_text: str = Field(..., min_length=10, max_length=MAX_TALE_CHARACTERS, description="Texte du conte en français")
    story_id: str = Field(default="conte_web", description="Identifiant unique du conte")
    profile: str = Field(default="research", description="research ou commercial")
    territory: str = Field(default="EU", description="Code territoire ISO")
    style_preset: str = Field(default="watercolor_mythology", description="Clé du preset de style")
    style_suffix: Optional[str] = None


def _generation_payload(
    *,
    story_id: str,
    story_path: Path,
    characters_dir: Path,
    output_dir: Path,
    profile: DeploymentProfile,
    territory: str,
    style_preset: str,
    style_suffix: str,
) -> dict[str, str]:
    """Construit le contrat sérialisable transmis au worker RQ."""
    return {
        "story_id": story_id,
        "story_path": str(story_path),
        "characters_dir": str(characters_dir),
        "output_dir": str(output_dir),
        "profile": profile.value,
        "territory": territory,
        "style_preset": style_preset,
        "style_suffix": style_suffix,
    }


def _enqueue_or_503(payload: dict[str, str]) -> dict[str, Any]:
    """Soumet un job et masque les détails de connectivité Redis au client."""
    try:
        job = enqueue_generation(payload)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="File de génération indisponible.") from exc
    return {
        "job_id": job.id,
        "status": "queued",
        "story_id": payload["story_id"],
        "status_url": f"/api/jobs/{job.id}",
    }


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
    run_dir = _existing_run_dir(story_id)
    bible_path = run_dir / "character_bible.json"
    if not bible_path.exists():
        raise HTTPException(status_code=404, detail="Bible non trouvée")
    return json.loads(bible_path.read_text(encoding="utf-8"))


@app.get("/api/runs/{story_id}/storyboard")
def get_storyboard(story_id: str):
    """Retourne le storyboard validé du run."""
    run_dir = _existing_run_dir(story_id)
    sb_path = run_dir / "storyboard.validated.json"
    if not sb_path.exists():
        sb_path = run_dir / "storyboard.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard non trouvé")
    return json.loads(sb_path.read_text(encoding="utf-8"))


@app.put("/api/runs/{story_id}/segments/{scene_id}")
def update_segment(
    story_id: str,
    scene_id: str,
    req: SegmentUpdateRequest,
    _: None = Depends(require_api_key),
):
    """Met à jour un segment du storyboard (Human-in-the-Loop)."""
    run_dir = _existing_run_dir(story_id)
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
def reorder_segments(
    story_id: str,
    req: SegmentsReorderRequest,
    _: None = Depends(require_api_key),
):
    """Réordonne les segments du storyboard."""
    run_dir = _existing_run_dir(story_id)
    sb_path = run_dir / "storyboard.validated.json"
    if not sb_path.exists():
        sb_path = run_dir / "storyboard.json"
    if not sb_path.exists():
        raise HTTPException(status_code=404, detail="Storyboard introuvable")

    sb_data = json.loads(sb_path.read_text(encoding="utf-8"))
    storyboard = Storyboard.model_validate(sb_data)
    seg_map = {s.scene_id: s for s in storyboard.segments}
    requested_ids = req.scene_ids_in_order

    if len(requested_ids) != len(seg_map) or set(requested_ids) != set(seg_map):
        raise HTTPException(
            status_code=422,
            detail="Le réordonnancement doit contenir chaque scène exactement une fois.",
        )

    new_segments = []
    for idx, sid in enumerate(requested_ids, start=1):
        seg = seg_map[sid]
        seg.ordre = idx
        new_segments.append(seg)

    storyboard.segments = new_segments
    revalidated = storyboard.model_validate(storyboard.model_dump())
    tmp_path = sb_path.with_suffix(f"{sb_path.suffix}.tmp")
    tmp_path.write_text(revalidated.model_dump_json(indent=2), encoding="utf-8")
    tmp_path.replace(sb_path)
    return {"status": "REORDERED", "total_segments": len(new_segments)}


@app.get("/api/runs/{story_id}/qc")
def get_qc_reports(story_id: str):
    """Retourne l'ensemble des rapports QC du run."""
    run_dir = _existing_run_dir(story_id)
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
    run_dir = _existing_run_dir(story_id)
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
    run_dir = _existing_run_dir(story_id)
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
    run_dir = _existing_run_dir(story_id)
    video_path = run_dir / "conte_final.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Vidéo finale non trouvée")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{story_id}_final.mp4")


@app.get("/api/media/{story_id}/subtitles/{ext}")
def get_subtitles_file(story_id: str, ext: str):
    """Sert les sous-titres SRT ou ASS."""
    if ext not in ALLOWED_SUBTITLE_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Format de sous-titre non pris en charge")
    run_dir = _existing_run_dir(story_id)
    sub_path = run_dir / "subtitles" / f"conte.{ext}"
    if not sub_path.exists():
        raise HTTPException(status_code=404, detail=f"Sous-titre .{ext} introuvable")
    media_type = "text/plain" if ext == "srt" else "text/x-ssa"
    return FileResponse(sub_path, media_type=media_type, filename=f"{story_id}.{ext}")


@app.post("/api/upload-and-run", status_code=202)
async def upload_and_run(
    _: None = Depends(require_api_key),
    story_id: str = Form("conte_custom"),
    tale_text: str = Form(...),
    profile: str = Form("research"),
    territory: str = Form("EU"),
    style_preset: str = Form("watercolor_mythology"),
    character_files: List[UploadFile] = File(default=[])
):
    """Endpoint complet d'importation de fichiers et de lancement de génération."""
    if len(tale_text) > MAX_TALE_CHARACTERS:
        raise HTTPException(status_code=413, detail="Texte du conte trop volumineux.")

    output_dir = _run_dir(story_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarde du texte
    story_file = output_dir / "conte.txt"
    story_file.write_text(tale_text, encoding="utf-8")

    # Sauvegarde des images de personnages uploadées
    chars_dir = output_dir / "personnages"
    chars_dir.mkdir(parents=True, exist_ok=True)

    if len(character_files) > MAX_CHARACTER_FILES:
        raise HTTPException(status_code=422, detail=f"Maximum {MAX_CHARACTER_FILES} images de personnages autorisées.")

    if character_files:
        for f in character_files:
            if not f.filename:
                continue
            filename = Path(f.filename).name
            suffix = Path(filename).suffix.lower()
            if suffix not in ALLOWED_IMAGE_EXTENSIONS or f.content_type not in ALLOWED_IMAGE_MEDIA_TYPES:
                raise HTTPException(status_code=422, detail="Format image non pris en charge.")

            content = await f.read(MAX_UPLOAD_BYTES + 1)
            if len(content) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Image trop volumineuse.")
            if not content:
                raise HTTPException(status_code=422, detail="Image vide.")
            try:
                with Image.open(BytesIO(content)) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError) as exc:
                raise HTTPException(status_code=422, detail="Le contenu uploadé n'est pas une image valide.") from exc

            target_file = (chars_dir / filename).resolve()
            if not target_file.is_relative_to(chars_dir.resolve()):
                raise HTTPException(status_code=422, detail="Nom de fichier invalide.")
            target_file.write_bytes(content)
    else:
        # Copie des fixtures par défaut si aucun upload
        fixture_chars = FIXTURES_ROOT / "personnages"
        if fixture_chars.exists():
            for p in fixture_chars.glob("*.png"):
                shutil.copy(p, chars_dir / p.name)

    preset_obj = StylePresetRegistry.get_preset(style_preset)
    dep_profile = DeploymentProfile.COMMERCIAL if profile == "commercial" else DeploymentProfile.RESEARCH

    return _enqueue_or_503(
        _generation_payload(
            story_id=story_id,
            story_path=story_file,
            characters_dir=chars_dir,
            output_dir=output_dir,
            profile=dep_profile,
            territory=territory,
            style_preset=style_preset,
            style_suffix=preset_obj.prompt_suffix,
        )
    )


@app.post("/api/generate", status_code=202)
def trigger_generation(req: TaleRunRequest, _: None = Depends(require_api_key)):
    """Déclenche la génération d'un conte animé (JSON payload)."""
    output_dir = _run_dir(req.story_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    story_file = output_dir / "conte.txt"
    story_file.write_text(req.tale_text, encoding="utf-8")

    chars_dir = FIXTURES_ROOT / "personnages"
    preset_obj = StylePresetRegistry.get_preset(req.style_preset)
    profile = DeploymentProfile.COMMERCIAL if req.profile == "commercial" else DeploymentProfile.RESEARCH

    return _enqueue_or_503(
        _generation_payload(
            story_id=req.story_id,
            story_path=story_file,
            characters_dir=chars_dir,
            output_dir=output_dir,
            profile=profile,
            territory=req.territory,
            style_preset=req.style_preset,
            style_suffix=req.style_suffix or preset_obj.prompt_suffix,
        )
    )


@app.get("/api/jobs/{job_id}")
def get_generation_job(job_id: str) -> dict[str, Any]:
    """Retourne l'état durable d'une génération asynchrone."""
    try:
        return job_response(get_job(job_id))
    except (NoSuchJobError, RedisError) as exc:
        raise HTTPException(status_code=404, detail="Job introuvable ou file indisponible.") from exc


@app.post("/api/jobs/{job_id}/cancel", dependencies=[Depends(require_api_key)])
def cancel_generation_job(job_id: str) -> dict[str, Any]:
    """Annule un job encore en file ; un rendu déjà démarré reste non interruptible."""
    try:
        result = cancel_job(job_id)
    except (NoSuchJobError, RedisError) as exc:
        raise HTTPException(status_code=404, detail="Job introuvable ou file indisponible.") from exc
    if not result["cancelled"]:
        raise HTTPException(status_code=409, detail="Le job est déjà démarré ou terminé.")
    return {"job_id": job_id, **result}


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Page d'accueil de l'API, sans redirection vers un localhost du serveur."""
    return """<!DOCTYPE html>
<html lang="fr">
<head><title>MangaTok Studio API</title></head>
<body style="background:#090A0F; color:#FFF; font-family:sans-serif; text-align:center; padding:50px;">
  <h1>⚡ MangaTok Studio — Mode « Conte animé » API</h1>
  <p>Le dashboard est servi séparément par le frontend configuré pour cet environnement.</p>
  <p><a href="/docs" style="color:#3B82F6;">Documentation Swagger API</a></p>
</body>
</html>"""
