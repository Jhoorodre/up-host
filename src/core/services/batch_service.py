"""
Batch Upload System for Multiple Manga Operations
Handles queuing, processing, and monitoring of bulk upload operations
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from core.models import Manga


class BatchJobStatus(Enum):
    """Batch job status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class BatchJobType(Enum):
    """Types of batch operations"""
    UPLOAD = "upload"
    RESCAN = "rescan"
    METADATA_UPDATE = "metadata_update"
    CACHE_REFRESH = "cache_refresh"


@dataclass
class BatchJobItem:
    """Individual item within a batch job"""
    item_id: str
    manga_title: str
    manga_path: str
    chapters_selected: List[str]  # Chapter names
    status: BatchJobStatus = BatchJobStatus.PENDING
    progress: float = 0.0  # 0-100
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    upload_results: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Duration of processing in seconds"""
        if not self.start_time:
            return 0.0
        end_time = self.completion_time or time.time()
        return end_time - self.start_time
    
    @property
    def is_complete(self) -> bool:
        """Check if item is in a final state"""
        return self.status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED, BatchJobStatus.CANCELLED]


@dataclass
class BatchJob:
    """Complete batch upload job"""
    job_id: str
    job_type: BatchJobType
    title: str
    description: str
    items: List[BatchJobItem] = field(default_factory=list)
    status: BatchJobStatus = BatchJobStatus.PENDING
    created_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    total_progress: float = 0.0  # Overall job progress 0-100
    metadata_template: Optional[Dict[str, Any]] = None
    
    @property
    def duration_seconds(self) -> float:
        """Total job duration in seconds"""
        if not self.start_time:
            return 0.0
        end_time = self.completion_time or time.time()
        return end_time - self.start_time
    
    @property
    def items_pending(self) -> int:
        """Number of pending items"""
        return sum(1 for item in self.items if item.status == BatchJobStatus.PENDING)
    
    @property
    def items_running(self) -> int:
        """Number of running items"""
        return sum(1 for item in self.items if item.status == BatchJobStatus.RUNNING)
    
    @property
    def items_completed(self) -> int:
        """Number of completed items"""
        return sum(1 for item in self.items if item.status == BatchJobStatus.COMPLETED)
    
    @property
    def items_failed(self) -> int:
        """Number of failed items"""
        return sum(1 for item in self.items if item.status == BatchJobStatus.FAILED)
    
    @property
    def success_rate(self) -> float:
        """Success rate percentage"""
        total_processed = self.items_completed + self.items_failed
        if total_processed == 0:
            return 0.0
        return (self.items_completed / total_processed) * 100.0


class BatchService:
    """
    Comprehensive batch upload service
    
    Features:
    - Queue management for multiple batch jobs
    - Concurrent processing with configurable limits
    - Progress tracking and status updates
    - Job prioritization and dependency handling
    - Pause/resume functionality
    - Comprehensive error handling and recovery
    - Statistics and performance monitoring
    """
    
    def __init__(self, max_concurrent_jobs: int = 2, max_concurrent_items: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_concurrent_items = max_concurrent_items
        
        # Job storage
        self.jobs: Dict[str, BatchJob] = {}
        self.job_queue: asyncio.Queue = asyncio.Queue()
        
        # Processing control
        self._is_running = False
        self._worker_tasks: List[asyncio.Task] = []
        self._lifecycle_lock = asyncio.Lock()
        self._job_semaphore = asyncio.Semaphore(max_concurrent_jobs)
        self._item_semaphore = asyncio.Semaphore(max_concurrent_items)
        
        # Callbacks
        self._job_progress_callback: Optional[Callable[[str, float], None]] = None
        self._job_completed_callback: Optional[Callable[[str, BatchJob], None]] = None
        self._item_completed_callback: Optional[Callable[[str, str, BatchJobItem], None]] = None
        
        logger.info(f"BatchService initialized: {max_concurrent_jobs} concurrent jobs, "
                   f"{max_concurrent_items} concurrent items")
    
    async def start_service(self):
        """Start the batch processing service"""
        async with self._lifecycle_lock:
            if self._is_running:
                logger.warning("Batch service already running")
                return

            self._is_running = True

            # Start worker tasks
            for i in range(self.max_concurrent_jobs):
                task = asyncio.create_task(self._job_worker(f"worker-{i}"))
                self._worker_tasks.append(task)

            logger.info(f"Batch service started with {len(self._worker_tasks)} workers")
    
    async def stop_service(self):
        """Stop the batch processing service"""
        async with self._lifecycle_lock:
            if not self._is_running:
                return

            self._is_running = False

            # Normalize active job states before worker cancellation.
            paused_jobs = 0
            for job in self.jobs.values():
                if job.status != BatchJobStatus.RUNNING:
                    continue

                paused_jobs += 1
                job.status = BatchJobStatus.PAUSED
                for item in job.items:
                    if item.status == BatchJobStatus.RUNNING:
                        item.status = BatchJobStatus.PAUSED
                        item.completion_time = None

            # Drain queued job ids and return queued jobs to pending for future resume/start.
            returned_to_pending = 0
            while True:
                try:
                    queued_job_id = self.job_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                queued_job = self.jobs.get(queued_job_id)
                if queued_job and queued_job.status == BatchJobStatus.QUEUED:
                    queued_job.status = BatchJobStatus.PENDING
                    returned_to_pending += 1
                self.job_queue.task_done()

            # Cancel all worker tasks
            for task in self._worker_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self._worker_tasks:
                await asyncio.gather(*self._worker_tasks, return_exceptions=True)

            self._worker_tasks.clear()
            if paused_jobs or returned_to_pending:
                logger.info(
                    f"Batch service state normalized on stop: {paused_jobs} running->paused, "
                    f"{returned_to_pending} queued->pending"
                )
            logger.info("Batch service stopped")
    
    def create_upload_job(
        self,
        title: str,
        manga_list: List[Dict[str, Any]],
        description: str = ""
    ) -> str:
        """
        Create a new batch upload job
        
        Args:
            title: Job title
            manga_list: List of manga with selected chapters
                       Format: [{"manga": Manga, "chapters": [Chapter]}]
            description: Job description
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Create job items
        items = []
        for manga_data in manga_list:
            manga = manga_data["manga"]
            selected_chapters = manga_data.get("chapters", [])
            
            item = BatchJobItem(
                item_id=str(uuid.uuid4()),
                manga_title=manga.title,
                manga_path=str(manga.path),
                chapters_selected=[ch.name for ch in selected_chapters],
            )
            items.append(item)
        
        # Create batch job
        job = BatchJob(
            job_id=job_id,
            job_type=BatchJobType.UPLOAD,
            title=title,
            description=description or f"Batch upload of {len(items)} manga",
            items=items
        )
        
        self.jobs[job_id] = job
        
        logger.info(f"Created batch upload job '{title}': {len(items)} items")
        return job_id
    
    def create_metadata_job(
        self,
        title: str,
        manga_list: List[Manga],
        metadata_template: Dict[str, Any],
        description: str = ""
    ) -> str:
        """
        Create a batch metadata update job
        
        Args:
            title: Job title
            manga_list: List of manga to update
            metadata_template: Metadata template to apply
            description: Job description
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Create job items
        items = []
        for manga in manga_list:
            item = BatchJobItem(
                item_id=str(uuid.uuid4()),
                manga_title=manga.title,
                manga_path=str(manga.path),
                chapters_selected=[],  # Not applicable for metadata
            )
            items.append(item)
        
        # Create batch job
        job = BatchJob(
            job_id=job_id,
            job_type=BatchJobType.METADATA_UPDATE,
            title=title,
            description=description or f"Batch metadata update for {len(items)} manga",
            items=items
        )
        
        # Store metadata template in job data
        job.metadata_template = metadata_template
        
        self.jobs[job_id] = job
        
        logger.info(f"Created batch metadata job '{title}': {len(items)} items")
        return job_id
    
    async def submit_job(self, job_id: str) -> bool:
        """
        Submit a job for processing
        
        Args:
            job_id: Job ID to submit
            
        Returns:
            True if submitted successfully, False otherwise
        """
        if job_id not in self.jobs:
            logger.error(f"Job not found: {job_id}")
            return False

        if not self._is_running:
            logger.warning(f"Batch service was stopped; auto-starting before submit for job {job_id}")
            await self.start_service()
        
        job = self.jobs[job_id]
        if job.status != BatchJobStatus.PENDING:
            logger.warning(f"Job {job_id} is not in pending state: {job.status}")
            return False
        
        try:
            job.status = BatchJobStatus.QUEUED
            await self.job_queue.put(job_id)
            logger.info(f"Job submitted to queue: {job.title}")
            return True
        except Exception as e:
            # Roll back queue transition when enqueue fails.
            job.status = BatchJobStatus.PENDING
            logger.error(f"Error submitting job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """
        Pause a running job
        
        Args:
            job_id: Job ID to pause
            
        Returns:
            True if paused successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        if job.status == BatchJobStatus.RUNNING:
            job.status = BatchJobStatus.PAUSED
            logger.info(f"Job paused: {job.title}")
            return True
        
        return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        Resume a paused job by returning it to pending state.
        
        Args:
            job_id: Job ID to resume
            
        Returns:
            True if resumed successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        if job.status == BatchJobStatus.PAUSED:
            # Resume is implemented as re-queuing the job from pending state.
            job.status = BatchJobStatus.PENDING
            for item in job.items:
                if item.status == BatchJobStatus.PAUSED:
                    item.status = BatchJobStatus.PENDING
                    item.start_time = None
                    item.completion_time = None
            logger.info(f"Job resumed: {job.title}")
            return True
        
        return False
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        if job.status in [BatchJobStatus.PENDING, BatchJobStatus.QUEUED, BatchJobStatus.RUNNING, BatchJobStatus.PAUSED]:
            job.status = BatchJobStatus.CANCELLED
            job.completion_time = time.time()
            
            # Cancel all pending items
            for item in job.items:
                if not item.is_complete:
                    item.status = BatchJobStatus.CANCELLED
            
            logger.info(f"Job cancelled: {job.title}")
            return True
        
        return False
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[BatchJob]:
        """Get all jobs"""
        return list(self.jobs.values())
    
    def get_jobs_by_status(self, status: BatchJobStatus) -> List[BatchJob]:
        """Get jobs by status"""
        return [job for job in self.jobs.values() if job.status == status]
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        running_jobs = len(self.get_jobs_by_status(BatchJobStatus.RUNNING))
        pending_jobs = len(self.get_jobs_by_status(BatchJobStatus.PENDING))
        queued_jobs = len(self.get_jobs_by_status(BatchJobStatus.QUEUED))
        # asyncio.Queue can still contain stale IDs for jobs cancelled while queued.
        # UI/status should reflect effective queued jobs, not raw internal queue length.
        effective_queue_size = queued_jobs
        
        return {
            "service_running": self._is_running,
            "queue_size": effective_queue_size,
            "running_jobs": running_jobs,
            "pending_jobs": pending_jobs,
            "queued_jobs": queued_jobs,
            "total_jobs": len(self.jobs),
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "max_concurrent_items": self.max_concurrent_items
        }
    
    def set_callbacks(
        self,
        job_progress_callback: Optional[Callable[[str, float], None]] = None,
        job_completed_callback: Optional[Callable[[str, BatchJob], None]] = None,
        item_completed_callback: Optional[Callable[[str, str, BatchJobItem], None]] = None
    ):
        """Set callbacks for batch operations"""
        self._job_progress_callback = job_progress_callback
        self._job_completed_callback = job_completed_callback
        self._item_completed_callback = item_completed_callback
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a completed or cancelled job
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        if job.status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED, BatchJobStatus.CANCELLED]:
            del self.jobs[job_id]
            logger.info(f"Job deleted: {job.title}")
            return True
        
        logger.warning(f"Cannot delete active job: {job.title}")
        return False
    
    # Private methods
    
    async def _job_worker(self, worker_name: str):
        """Worker task for processing batch jobs"""
        logger.debug(f"Batch worker {worker_name} started")
        
        while self._is_running:
            try:
                # Get job from queue (with timeout to allow service stop)
                try:
                    job_id = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                try:
                    if job_id not in self.jobs:
                        logger.warning(f"Job not found in worker: {job_id}")
                        continue

                    # Process the job
                    await self._process_job(job_id, worker_name)
                finally:
                    self.job_queue.task_done()
                
            except asyncio.CancelledError:
                logger.debug(f"Batch worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in batch worker {worker_name}: {e}")
        
        logger.debug(f"Batch worker {worker_name} stopped")
    
    async def _process_job(self, job_id: str, worker_name: str):
        """Process a single batch job"""
        async with self._job_semaphore:
            job = self.jobs[job_id]

            if job.status == BatchJobStatus.CANCELLED:
                job.completion_time = time.time()
                logger.info(f"Worker {worker_name} skipping cancelled job: {job.title}")
                return

            if job.status == BatchJobStatus.PAUSED:
                logger.info(f"Worker {worker_name} skipping paused job: {job.title}")
                return

            if job.status not in {BatchJobStatus.QUEUED, BatchJobStatus.PENDING}:
                logger.info(f"Worker {worker_name} skipping non-runnable job state {job.status.value}: {job.title}")
                return
            
            logger.info(f"Worker {worker_name} starting job: {job.title}")
            
            # Update job status
            job.status = BatchJobStatus.RUNNING
            job.start_time = time.time()
            
            try:
                if job.job_type == BatchJobType.UPLOAD:
                    await self._process_upload_job(job)
                elif job.job_type == BatchJobType.METADATA_UPDATE:
                    await self._process_metadata_job(job)
                else:
                    raise ValueError(f"Unknown job type: {job.job_type}")
                
                if job.status == BatchJobStatus.CANCELLED:
                    job.completion_time = time.time()
                    logger.info(f"Job cancelled during processing: {job.title}")
                elif job.status == BatchJobStatus.PAUSED:
                    logger.info(f"Job paused during processing: {job.title}")
                else:
                    failed_items = any(item.status == BatchJobStatus.FAILED for item in job.items)
                    # Mark job with final state based on processed item outcomes.
                    job.status = BatchJobStatus.FAILED if failed_items else BatchJobStatus.COMPLETED
                    job.completion_time = time.time()

                    if failed_items:
                        logger.warning(
                            f"Job finished with failures: {job.title} ({job.duration_seconds:.1f}s, "
                            f"{job.success_rate:.1f}% success rate)"
                        )
                    else:
                        job.total_progress = 100.0
                        logger.success(f"Job completed: {job.title} ({job.duration_seconds:.1f}s, "
                                      f"{job.success_rate:.1f}% success rate)")
                
            except Exception as e:
                job.status = BatchJobStatus.FAILED
                job.completion_time = time.time()
                logger.error(f"Job failed: {job.title} - {e}")
            
            # Notify completion
            if self._job_completed_callback:
                try:
                    self._job_completed_callback(job_id, job)
                except Exception as e:
                    logger.error(f"Error in job completion callback: {e}")
    
    async def _process_upload_job(self, job: BatchJob):
        """Process batch upload job"""
        total_items = len(job.items)
        if total_items == 0:
            job.total_progress = 100.0
            return

        # Create tasks for all items
        tasks = []
        for item in job.items:
            if job.status == BatchJobStatus.CANCELLED:
                break
            if job.status == BatchJobStatus.PAUSED:
                break
            if item.status != BatchJobStatus.PENDING:
                continue
            
            task = asyncio.create_task(self._process_upload_item(job, item))
            tasks.append(task)
        
        # Process items with concurrency control
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update job progress
        completed_items = sum(1 for item in job.items if item.status == BatchJobStatus.COMPLETED)
        job.total_progress = (completed_items / total_items) * 100.0
    
    async def _process_upload_item(self, job: BatchJob, item: BatchJobItem):
        """Process a single upload item"""
        async with self._item_semaphore:
            if item.status != BatchJobStatus.PENDING:
                return

            if job.status in [BatchJobStatus.CANCELLED, BatchJobStatus.PAUSED]:
                item.status = BatchJobStatus.PAUSED if job.status == BatchJobStatus.PAUSED else BatchJobStatus.CANCELLED
                return
            
            item.status = BatchJobStatus.RUNNING
            item.start_time = time.time()
            
            try:
                # Simulate upload process (replace with actual upload logic)
                # Load manga and chapters
                # This would integrate with the actual upload service
                
                # Simulate upload with progress
                for progress in range(0, 101, 10):
                    if job.status == BatchJobStatus.CANCELLED:
                        item.status = BatchJobStatus.CANCELLED
                        return
                    if job.status == BatchJobStatus.PAUSED:
                        item.status = BatchJobStatus.PAUSED
                        return
                    
                    item.progress = float(progress)
                    await asyncio.sleep(0.1)  # Simulate work
                
                # Mark as completed
                item.status = BatchJobStatus.COMPLETED
                item.completion_time = time.time()
                item.progress = 100.0
                
                logger.debug(f"Upload item completed: {item.manga_title}")
                
            except Exception as e:
                item.status = BatchJobStatus.FAILED
                item.error_message = str(e)
                item.completion_time = time.time()
                logger.error(f"Upload item failed: {item.manga_title} - {e}")
            
            # Update job progress
            total_items = len(job.items)
            if total_items > 0:
                completed_items = sum(1 for i in job.items if i.status == BatchJobStatus.COMPLETED)
                job.total_progress = (completed_items / total_items) * 100.0
            
            # Notify progress
            if self._job_progress_callback:
                try:
                    self._job_progress_callback(job.job_id, job.total_progress)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
            
            # Notify item completion
            if self._item_completed_callback:
                try:
                    self._item_completed_callback(job.job_id, item.item_id, item)
                except Exception as e:
                    logger.error(f"Error in item completion callback: {e}")
    
    async def _process_metadata_job(self, job: BatchJob):
        """Process batch metadata update job"""
        # Similar to upload processing but for metadata updates
        # This would integrate with the metadata update service

        total_items = len(job.items)
        if total_items == 0:
            job.total_progress = 100.0
            return
        
        for item in job.items:
            if job.status == BatchJobStatus.CANCELLED:
                break
            if job.status == BatchJobStatus.PAUSED:
                item.status = BatchJobStatus.PAUSED
                break
            if item.status != BatchJobStatus.PENDING:
                continue
            
            item.status = BatchJobStatus.RUNNING
            item.start_time = time.time()
            
            try:
                # Simulate metadata update
                await asyncio.sleep(0.5)

                # Handle mid-flight control transitions triggered while sleeping.
                if job.status == BatchJobStatus.CANCELLED:
                    item.status = BatchJobStatus.CANCELLED
                    item.completion_time = time.time()
                    continue
                if job.status == BatchJobStatus.PAUSED:
                    item.status = BatchJobStatus.PAUSED
                    item.completion_time = None
                    continue
                
                item.status = BatchJobStatus.COMPLETED
                item.completion_time = time.time()
                item.progress = 100.0
                
            except Exception as e:
                item.status = BatchJobStatus.FAILED
                item.error_message = str(e)
                item.completion_time = time.time()
        
        # Update job progress
        completed_items = sum(1 for item in job.items if item.status == BatchJobStatus.COMPLETED)
        job.total_progress = (completed_items / total_items) * 100.0