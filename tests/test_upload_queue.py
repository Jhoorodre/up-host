import asyncio

from core.services.queue import UploadQueue


async def test_concurrent_start_does_not_duplicate_workers() -> None:
    queue = UploadQueue(max_concurrent=2)

    await asyncio.gather(queue.start(), queue.start(), queue.start())

    assert queue.running is True
    assert len(queue.workers) == 2

    await queue.stop()


async def test_add_job_rejected_after_concurrent_stop() -> None:
    queue = UploadQueue(max_concurrent=1)
    await queue.start()

    # Trigger stop and race an add request against lifecycle transition.
    stop_task = asyncio.create_task(queue.stop())
    await asyncio.sleep(0)

    add_failed = False
    try:
        await queue.add_job(lambda: None)
    except RuntimeError:
        add_failed = True

    await stop_task
    assert queue.running is False
    assert add_failed is True or any(job.status.value in {"failed", "completed"} for job in queue.jobs.values())
    assert all(job.status.value != "pending" for job in queue.jobs.values())
