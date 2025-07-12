import asyncio
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time
from loguru import logger


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    task: Callable
    args: tuple
    kwargs: dict
    status: JobStatus = JobStatus.PENDING
    result: Any = None
    error: str = None
    created_at: float = None
    started_at: float = None
    completed_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class UploadQueue:
    """Async queue for managing upload jobs"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.queue: asyncio.Queue = asyncio.Queue()
        self.jobs: Dict[str, Job] = {}
        self.workers: List[asyncio.Task] = []
        self.running = False
        self._job_counter = 0
    
    async def start(self):
        """Start queue workers"""
        if self.running:
            return
        
        self.running = True
        logger.info(f"Starting upload queue with {self.max_concurrent} workers")
        
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """Stop all workers gracefully"""
        if not self.running:
            return
            
        self.running = False
        logger.info("Stopping upload queue...")
        
        # Cancel all workers
        for worker in self.workers:
            if not worker.done():
                worker.cancel()
        
        # Wait for workers to finish with timeout
        if self.workers:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.workers, return_exceptions=True),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                logger.warning("Workers didn't stop within timeout, forcing shutdown")
        
        self.workers.clear()
        logger.info("Upload queue stopped")
    
    async def add_job(self, task: Callable, *args, **kwargs) -> str:
        """Add a job to the queue"""
        self._job_counter += 1
        job_id = f"job-{self._job_counter}"
        
        job = Job(
            id=job_id,
            task=task,
            args=args,
            kwargs=kwargs
        )
        
        self.jobs[job_id] = job
        await self.queue.put(job)
        
        logger.debug(f"Job {job_id} added to queue")
        return job_id
    
    async def get_job_status(self, job_id: str) -> JobStatus:
        """Get the status of a job"""
        if job_id in self.jobs:
            return self.jobs[job_id].status
        return None
    
    async def get_job_result(self, job_id: str) -> Any:
        """Get the result of a completed job"""
        if job_id in self.jobs and self.jobs[job_id].status == JobStatus.COMPLETED:
            return self.jobs[job_id].result
        return None
    
    async def wait_for_job(self, job_id: str, timeout: float = None) -> Job:
        """Wait for a job to complete"""
        start_time = time.time()
        
        while job_id in self.jobs:
            job = self.jobs[job_id]
            
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                return job
            
            if timeout and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError(f"Job {job_id} timed out")
            
            await asyncio.sleep(0.1)
        
        return None
    
    async def _worker(self, worker_name: str):
        """Worker coroutine"""
        logger.debug(f"{worker_name} started")
        
        try:
            while self.running:
                # Get job from queue
                job = await self.queue.get()
                
                if job is None:  # Stop signal
                    break
                
                # Process job
                job.status = JobStatus.RUNNING
                job.started_at = time.time()
                
                try:
                    logger.debug(f"{worker_name} processing {job.id}")
                    
                    # Execute the task
                    if asyncio.iscoroutinefunction(job.task):
                        result = await job.task(*job.args, **job.kwargs)
                    else:
                        result = await asyncio.to_thread(job.task, *job.args, **job.kwargs)
                    
                    job.result = result
                    job.status = JobStatus.COMPLETED
                    job.completed_at = time.time()
                    
                    logger.debug(f"{worker_name} completed {job.id}")
                    
                except Exception as e:
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    job.completed_at = time.time()
                    
                    logger.error(f"{worker_name} failed {job.id}: {e}")
                
                finally:
                    self.queue.task_done()
        
        except asyncio.CancelledError:
            logger.debug(f"{worker_name} cancelled")
            raise
        
        logger.debug(f"{worker_name} stopped")