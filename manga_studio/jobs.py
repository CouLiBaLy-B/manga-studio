"""File durable Redis/RQ pour les générations longues de MangaTok Studio."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from redis import Redis
from rq import Queue
from rq.job import Job, get_current_job
from manga_studio.core.models.config import DeploymentProfile, TalePipelineConfig
from manga_studio.pipeline.runner import AnimatedTalePipelineRunner

QUEUE_NAME = os.getenv("MANGA_STUDIO_QUEUE_NAME", "manga-studio")
REDIS_URL = os.getenv("MANGA_STUDIO_REDIS_URL", "redis://localhost:6379/0")
JOB_TIMEOUT_SECONDS = int(os.getenv("MANGA_STUDIO_JOB_TIMEOUT_SECONDS", "3600"))


def _connection() -> Redis:
    """Crée une connexion Redis contrôlée par la configuration runtime."""
    return Redis.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=5)


def _queue() -> Queue:
    return Queue(QUEUE_NAME, connection=_connection(), default_timeout=JOB_TIMEOUT_SECONDS)


def enqueue_generation(payload: dict[str, Any]) -> Job:
    """Place une génération en file sans exécuter de calcul dans le processus HTTP."""
    queue = _queue()
    return queue.enqueue(
        run_generation_job,
        payload,
        job_timeout=JOB_TIMEOUT_SECONDS,
        result_ttl=86_400,
        failure_ttl=604_800,
    )


def run_generation_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Exécute un job dans le worker et expose une progression minimale durable."""
    job = get_current_job()
    if job:
        job.meta.update({"progress": 5, "stage": "pipeline", "story_id": payload["story_id"]})
        job.save_meta()

    profile = DeploymentProfile(payload["profile"])
    config = TalePipelineConfig(
        story_path=Path(payload["story_path"]),
        characters_dir=Path(payload["characters_dir"]),
        output_dir=Path(payload["output_dir"]),
        profile=profile,
        territory=payload["territory"],
        style_preset=payload["style_preset"],
        style_suffix=payload["style_suffix"],
        enable_bedrock=False,
        enable_h3_local=False,
        generate_subtitles=True,
    )
    state = AnimatedTalePipelineRunner.run_pipeline(config=config, use_mock_video=True)
    result = {
        "status": state.get("status"),
        "story_id": payload["story_id"],
        "total_segments": len(state["validated_storyboard"].segments) if state.get("validated_storyboard") else 0,
        "video_url": f"/api/media/{payload['story_id']}/video",
        "subtitles_srt_url": f"/api/media/{payload['story_id']}/subtitles/srt",
        "subtitles_ass_url": f"/api/media/{payload['story_id']}/subtitles/ass",
    }
    if job:
        job.meta.update({"progress": 100, "stage": "completed", "result": result})
        job.save_meta()
    return result


def get_job(job_id: str) -> Job:
    """Récupère un job, en transformant les détails Redis en erreur HTTP appelante."""
    return Job.fetch(job_id, connection=_connection())


def job_response(job: Job) -> dict[str, Any]:
    """Sérialise uniquement les informations utiles et non sensibles d'un job RQ."""
    status = job.get_status(refresh=True)
    status_map = {
        "queued": "queued",
        "deferred": "queued",
        "scheduled": "queued",
        "started": "running",
        "finished": "completed",
        "failed": "failed",
        "stopped": "cancelled",
        "canceled": "cancelled",
    }
    result = job.result if status == "finished" and isinstance(job.result, dict) else None
    return {
        "job_id": job.id,
        "status": status_map.get(status, status),
        "progress": job.meta.get("progress", 0 if status in {"queued", "deferred"} else None),
        "stage": job.meta.get("stage"),
        "story_id": job.meta.get("story_id"),
        "result": result,
        "error": "La génération a échoué. Consultez les journaux du worker." if status == "failed" else None,
    }


def cancel_job(job_id: str) -> dict[str, Any]:
    """Annule un job non démarré ; RQ ne peut pas interrompre un rendu déjà actif sûrement."""
    job = get_job(job_id)
    status = job.get_status(refresh=True)
    if status not in {"queued", "deferred", "scheduled"}:
        return {"cancelled": False, "status": status}
    job.cancel()
    return {"cancelled": True, "status": "cancelled"}
