"""Tests unitaires de la file Redis/RQ sans nécessiter un serveur Redis."""

from types import SimpleNamespace

from manga_studio import jobs


class FakeWorkerJob:
    def __init__(self):
        self.meta = {}

    def save_meta(self):
        return None


def test_run_generation_job_publishes_safe_result(monkeypatch, tmp_path):
    worker_job = FakeWorkerJob()
    monkeypatch.setattr(jobs, "get_current_job", lambda: worker_job)
    storyboard = SimpleNamespace(segments=[object(), object()])
    monkeypatch.setattr(
        jobs.AnimatedTalePipelineRunner,
        "run_pipeline",
        lambda config, use_mock_video: {"status": "COMPLETED", "validated_storyboard": storyboard},
    )
    payload = {
        "story_id": "job-story",
        "story_path": str(tmp_path / "conte.txt"),
        "characters_dir": str(tmp_path / "personnages"),
        "output_dir": str(tmp_path / "output"),
        "profile": "research",
        "territory": "EU",
        "style_preset": "watercolor_mythology",
        "style_suffix": "test suffix",
    }

    result = jobs.run_generation_job(payload)

    assert result == {
        "status": "COMPLETED",
        "story_id": "job-story",
        "total_segments": 2,
        "video_url": "/api/media/job-story/video",
        "subtitles_srt_url": "/api/media/job-story/subtitles/srt",
        "subtitles_ass_url": "/api/media/job-story/subtitles/ass",
    }
    assert worker_job.meta["progress"] == 100
    assert worker_job.meta["stage"] == "completed"


def test_job_response_hides_internal_failure_details():
    fake_job = SimpleNamespace(
        id="job-1",
        meta={"progress": 5, "stage": "pipeline", "story_id": "story"},
        result=None,
        get_status=lambda refresh: "failed",
    )

    response = jobs.job_response(fake_job)

    assert response["status"] == "failed"
    assert "journaux du worker" in response["error"]
    assert "traceback" not in response["error"].lower()
