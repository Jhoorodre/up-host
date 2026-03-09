import asyncio
from pathlib import Path

from core.models import Manga
from core.services.batch_service import BatchJobStatus, BatchService


async def test_submit_job_sets_queued_and_blocks_duplicate(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)
    service._is_running = True

    manga = Manga(title="M1", path=tmp_path / "M1")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})

    first_submit = await service.submit_job(job_id)
    second_submit = await service.submit_job(job_id)

    assert first_submit is True
    assert second_submit is False
    queued_job = service.get_job(job_id)
    assert queued_job is not None
    assert queued_job.status == BatchJobStatus.QUEUED


async def test_submit_job_auto_starts_service(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga = Manga(title="M0", path=tmp_path / "M0")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})

    submitted = await service.submit_job(job_id)

    assert submitted is True
    status = service.get_queue_status()
    assert status["service_running"] is True
    assert status["queued_jobs"] == 1

    await service.stop_service()


async def test_concurrent_submit_auto_start_does_not_duplicate_workers(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga1 = Manga(title="M0A", path=tmp_path / "M0A")
    manga2 = Manga(title="M0B", path=tmp_path / "M0B")
    job1 = service.create_metadata_job("job1", [manga1], {"title": "x"})
    job2 = service.create_metadata_job("job2", [manga2], {"title": "x"})

    results = await asyncio.gather(service.submit_job(job1), service.submit_job(job2))

    assert results == [True, True]
    assert service.get_queue_status()["service_running"] is True
    assert len(service._worker_tasks) == service.max_concurrent_jobs

    await service.stop_service()


async def test_process_job_marks_failed_when_any_item_failed(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga = Manga(title="M2", path=tmp_path / "M2")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})
    job = service.get_job(job_id)
    assert job is not None

    # Simulate a prior item failure inside the batch.
    job.items[0].status = BatchJobStatus.FAILED
    job.status = BatchJobStatus.QUEUED

    await service._process_job(job_id, "test-worker")

    assert job.status == BatchJobStatus.FAILED


def test_cancel_job_accepts_queued_state(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga = Manga(title="M3", path=tmp_path / "M3")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})
    job = service.get_job(job_id)
    assert job is not None
    job.status = BatchJobStatus.QUEUED

    cancelled = service.cancel_job(job_id)

    assert cancelled is True
    assert job.status == BatchJobStatus.CANCELLED


async def test_cancelled_queued_job_not_counted_in_queue_size(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)
    service._is_running = True

    manga = Manga(title="M3Q", path=tmp_path / "M3Q")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})

    submitted = await service.submit_job(job_id)
    assert submitted is True

    cancelled = service.cancel_job(job_id)
    assert cancelled is True

    status = service.get_queue_status()
    assert status["queued_jobs"] == 0
    assert status["queue_size"] == 0


async def test_stop_service_returns_queued_to_pending(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)
    await service.start_service()

    manga = Manga(title="M4", path=tmp_path / "M4")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})

    submitted = await service.submit_job(job_id)
    assert submitted is True

    job = service.get_job(job_id)
    assert job is not None
    assert job.status == BatchJobStatus.QUEUED

    await service.stop_service()

    assert job.status == BatchJobStatus.PENDING


async def test_metadata_item_does_not_complete_if_cancelled_mid_flight(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga = Manga(title="M5", path=tmp_path / "M5")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})
    job = service.get_job(job_id)
    assert job is not None
    job.status = BatchJobStatus.RUNNING

    task = asyncio.create_task(service._process_metadata_job(job))
    await asyncio.sleep(0.1)
    job.status = BatchJobStatus.CANCELLED
    await task

    assert job.items[0].status == BatchJobStatus.CANCELLED


async def test_metadata_item_pauses_if_paused_mid_flight(tmp_path: Path) -> None:
    service = BatchService(max_concurrent_jobs=1, max_concurrent_items=1)

    manga = Manga(title="M6", path=tmp_path / "M6")
    job_id = service.create_metadata_job("job", [manga], {"title": "x"})
    job = service.get_job(job_id)
    assert job is not None
    job.status = BatchJobStatus.RUNNING

    task = asyncio.create_task(service._process_metadata_job(job))
    await asyncio.sleep(0.1)
    job.status = BatchJobStatus.PAUSED
    await task

    assert job.items[0].status == BatchJobStatus.PAUSED
