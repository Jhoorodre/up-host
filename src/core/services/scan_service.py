"""
Progressive Manga Library Scanning Service
Transforms blocking library loading into real-time progressive scanning
"""

import asyncio
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any, cast
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from core.models import Manga
from .cache_service import CacheService


@dataclass
class ScanResult:
    """Result of scanning a single manga folder"""
    manga: Optional[Manga]
    error: Optional[str] = None
    scan_time: float = 0.0
    path: Optional[Path] = None
    
    @property
    def success(self) -> bool:
        return self.manga is not None and self.error is None


@dataclass  
class ScanProgress:
    """Progress information for ongoing scan"""
    total_folders: int
    scanned_folders: int
    current_folder: str
    manga_found: int
    errors: int
    elapsed_time: float
    estimated_remaining: float
    
    @property
    def progress_percentage(self) -> int:
        if self.total_folders == 0:
            return 100
        return min(100, int((self.scanned_folders / self.total_folders) * 100))
    
    @property
    def scan_rate(self) -> float:
        """Folders per second"""
        if self.elapsed_time == 0:
            return 0.0
        return self.scanned_folders / self.elapsed_time


class ScanService:
    """
    Progressive manga library scanning service with worker pools and real-time feedback
    
    Features:
    - Non-blocking async scanning with configurable worker pools
    - Real-time progress updates via callbacks
    - Cancellation support for stopping scans mid-operation  
    - Incremental results - manga appear as they're discovered
    - Performance monitoring and optimization
    - Smart folder filtering to skip non-manga directories
    """
    
    def __init__(self, max_workers: int = 4, enable_cache: bool = True):
        self.max_workers = max_workers
        self.enable_cache = enable_cache
        self._executor = None
        self._scan_queue: Optional[asyncio.Queue] = None
        self._results_queue: Optional[asyncio.Queue] = None
        self._progress_callback: Optional[Callable[[ScanProgress], None]] = None
        self._result_callback: Optional[Callable[[ScanResult], None]] = None
        self._completion_callback: Optional[Callable[[List], None]] = None
        self._is_scanning = False
        self._cancel_requested = False
        
        # Cache service
        self.cache_service = CacheService() if enable_cache else None
        
        # Statistics
        self._scan_start_time = 0.0
        self._total_folders = 0
        self._scanned_folders = 0
        self._manga_found = 0
        self._errors = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Worker tracking for non-blocking operation
        self._active_worker_tasks: List[asyncio.Task[List[ScanResult]]] = []
        self._completed_workers = 0
        self._total_workers_count = 0
        self._scan_completion_future: Optional[asyncio.Future[Any]] = None
        self._all_worker_results: List[ScanResult] = []
        
        logger.info(f"ScanService initialized with {max_workers} workers, cache: {'enabled' if enable_cache else 'disabled'}")
    
    async def start_scan(
        self,
        root_path: Path,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        result_callback: Optional[Callable[[ScanResult], None]] = None,
        completion_callback: Optional[Callable[[List], None]] = None
    ) -> List[ScanResult]:
        """
        Start progressive manga library scan
        
        Args:
            root_path: Root directory to scan for manga
            progress_callback: Called with progress updates during scan
            result_callback: Called with each manga found (for incremental updates)
            
        Returns:
            List of all scan results
        """
        if self._is_scanning:
            logger.warning("Scan already in progress - ignoring new scan request")
            return []
        
        self._is_scanning = True
        self._cancel_requested = False
        self._progress_callback = progress_callback
        self._result_callback = result_callback
        self._completion_callback = completion_callback
        
        logger.info(f"Starting progressive library scan: {root_path}")
        
        try:
            # Initialize
            await self._initialize_scan()
            
            # Discover manga folders
            manga_folders = await self._discover_manga_folders(root_path)
            self._total_folders = len(manga_folders)
            
            if self._total_folders == 0:
                logger.warning(f"No manga folders found in {root_path}")
                self._is_scanning = False
                await self._cleanup_scan()
                if self._completion_callback:
                    try:
                        self._completion_callback([])
                    except Exception as cb_error:
                        logger.error(f"Error in completion callback: {cb_error}")
                return []
            
            logger.info(f"Found {self._total_folders} potential manga folders")
            
            # Reset statistics
            self._scan_start_time = time.time()
            self._scanned_folders = 0
            self._manga_found = 0
            self._errors = 0
            
            # Start scanning process (non-blocking)
            await self._scan_folders(manga_folders)
            
            # Return immediately - workers run in background, results via callbacks
            logger.info("Scan started successfully - workers running in background")
            return []  # Results will come via callbacks
            
        except Exception as e:
            logger.error(f"Error during library scan: {e}")
            self._is_scanning = False
            await self._cleanup_scan()
            if self._completion_callback:
                try:
                    self._completion_callback([])
                except Exception as cb_error:
                    logger.error(f"Error in completion callback: {cb_error}")
            return []
    
    async def cancel_scan(self):
        """Cancel the current scan operation"""
        if not self._is_scanning:
            logger.debug("No scan in progress to cancel")
            return
            
        logger.info("Cancelling library scan...")
        self._cancel_requested = True
        
        # Wait for scan to finish cleanup
        max_wait = 5.0  # Maximum wait time in seconds
        wait_start = time.time()
        
        while self._is_scanning and (time.time() - wait_start) < max_wait:
            await asyncio.sleep(0.1)
        
        if self._is_scanning:
            logger.warning("Scan did not cancel gracefully within timeout")
        else:
            logger.info("Scan cancelled successfully")
    
    async def _initialize_scan(self):
        """Initialize scan queues and executor"""
        self._scan_queue = asyncio.Queue()
        self._results_queue = asyncio.Queue()
        
        # Create thread pool executor for I/O operations
        self._executor = ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix="MangaScan"
        )
        
        logger.debug(f"Initialized scan with {self._max_workers} workers")
    
    async def _cleanup_scan(self):
        """Clean up scan resources"""
        if self._executor:
            executor = self._executor
            # Executor shutdown can block; move it off the event loop thread.
            if hasattr(asyncio, 'to_thread'):
                await asyncio.to_thread(executor.shutdown, True)
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, executor.shutdown, True)
            self._executor = None
            
        self._scan_queue = None
        self._results_queue = None
        
        logger.debug("Scan cleanup completed")

    async def _finalize_scan_lifecycle(self) -> None:
        """Finalize scan lifecycle by cleaning resources and unlocking new scans."""
        await self._cleanup_scan()
        self._is_scanning = False

    def _schedule_finalize_lifecycle(self) -> None:
        """Schedule scan lifecycle cleanup safely even during loop shutdown."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._finalize_scan_lifecycle())
            return
        except RuntimeError:
            logger.debug("No running loop available for async scan finalization; applying sync fallback")

        # Fallback when loop is no longer running (e.g. interpreter shutdown).
        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None
        self._scan_queue = None
        self._results_queue = None
        self._is_scanning = False
    
    async def _discover_manga_folders(self, root_path: Path) -> List[Path]:
        """
        Discover potential manga folders using smart filtering
        
        Args:
            root_path: Root directory to search
            
        Returns:
            List of paths that might contain manga
        """
        manga_folders = []
        
        if not root_path.exists() or not root_path.is_dir():
            logger.error(f"Root path does not exist or is not a directory: {root_path}")
            return []
        
        try:
            # Run folder discovery in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            manga_folders = await loop.run_in_executor(
                self._executor,
                self._discover_folders_sync,
                root_path
            )
            
            logger.debug(f"Discovered {len(manga_folders)} potential manga folders")
            return manga_folders
            
        except Exception as e:
            logger.error(f"Error discovering manga folders: {e}")
            return []
    
    def _discover_folders_sync(self, root_path: Path) -> List[Path]:
        """Synchronous folder discovery for thread execution"""
        manga_folders = []
        
        try:
            for item in root_path.iterdir():
                if not item.is_dir():
                    continue
                    
                # Skip hidden and system folders
                if item.name.startswith('.') or item.name.startswith('$'):
                    continue
                
                # Skip common non-manga folders
                skip_folders = {
                    'recycle.bin', 'system volume information',
                    'temp', 'tmp', 'cache', '.git', '.vscode'
                }
                if item.name.lower() in skip_folders:
                    continue
                
                # Check if folder might contain manga (has subdirectories or images)
                if self._is_potential_manga_folder(item):
                    manga_folders.append(item)
            
            # Sort by name for consistent ordering
            manga_folders.sort(key=lambda p: p.name.lower())
            
        except PermissionError:
            logger.warning(f"Permission denied accessing: {root_path}")
        except Exception as e:
            logger.error(f"Error in folder discovery: {e}")
        
        return manga_folders
    
    def _is_potential_manga_folder(self, folder_path: Path) -> bool:
        """Check if folder might contain manga chapters"""
        try:
            # Look for subdirectories (chapters) or image files
            has_subdirs = False
            has_images = False
            
            item_count = 0
            for item in folder_path.iterdir():
                item_count += 1
                if item_count > 50:  # Avoid scanning huge directories
                    break
                    
                if item.is_dir():
                    has_subdirs = True
                elif item.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
                    has_images = True
                
                # If we find both, it's likely a manga folder
                if has_subdirs and has_images:
                    return True
            
            # Return true if we found either chapters or images
            return has_subdirs or has_images
            
        except (PermissionError, OSError):
            return False
    
    @property
    def _max_workers(self) -> int:
        """Get current max workers with bounds checking"""
        return max(1, min(self.max_workers, 8))  # Limit to reasonable range
    
    async def _scan_folders(self, manga_folders: List[Path]) -> List[ScanResult]:
        """
        Scan manga folders with worker pool and progress reporting
        
        Args:
            manga_folders: List of folders to scan
            
        Returns:
            List of scan results
        """
        # BALANCED WORKER DISTRIBUTION - Replace semaphore with balanced chunks
        worker_assignments = self._distribute_folders_evenly(manga_folders, self._max_workers)
        
        # Log the balanced distribution
        for worker_id, folders in worker_assignments.items():
            folder_names = [f.name if isinstance(f, Path) else Path(f).name for f in folders]
            logger.info(f"Worker {worker_id} assigned {len(folders)} folders: {folder_names}")

        # Initialize tracking before creating tasks to avoid completion races.
        self._active_worker_tasks = []
        self._completed_workers = 0
        self._total_workers_count = 0
        self._all_worker_results = []
        
        # Create worker tasks with balanced assignments
        worker_tasks = []
        for worker_id, assigned_folders in worker_assignments.items():
            if assigned_folders:  # Only create task if worker has folders
                task = asyncio.create_task(
                    self._scan_worker_balanced(worker_id, assigned_folders)
                )
                worker_tasks.append(task)
        
        # Start workers without waiting for completion (non-blocking)
        if worker_tasks:
            logger.info(f"Started {len(worker_tasks)} workers in background - scan will continue asynchronously")
            
            # Set up completion callbacks for each worker
            for i, task in enumerate(worker_tasks):
                worker_id = i + 1

                def _done_callback(
                    done_task: asyncio.Task[List[ScanResult]],
                    current_worker_id: int = worker_id,
                ) -> None:
                    self._on_worker_completed(done_task, current_worker_id)

                task.add_done_callback(_done_callback)
        
        # Store worker tasks for tracking
        self._active_worker_tasks = worker_tasks
        self._total_workers_count = len(worker_tasks)
        
        # Return immediately - workers will report results via callbacks
        logger.debug("Scan workers started - workers will run independently")
        return []  # Results will be collected via callbacks
    
    def _on_worker_completed(self, task: asyncio.Task[List[ScanResult]], worker_id: int) -> None:
        """Handle individual worker completion"""
        try:
            self._completed_workers += 1

            if task.cancelled():
                self._errors += 1
                logger.debug(
                    f"Worker {worker_id} cancelled ({self._completed_workers}/{self._total_workers_count})"
                )
                if self._completed_workers >= self._total_workers_count:
                    self._finalize_scan()
                return
            
            # Get worker results
            worker_results = task.result()
            if isinstance(worker_results, list):
                # Store results and update statistics
                self._all_worker_results.extend(worker_results)
                for result in worker_results:
                    self._scanned_folders += 1
                    if result.success:
                        self._manga_found += 1
                    else:
                        self._errors += 1
            
            logger.debug(f"Worker {worker_id} completed ({self._completed_workers}/{self._total_workers_count})")
            
            # Check if all workers are done
            if self._completed_workers >= self._total_workers_count:
                self._finalize_scan()
                
        except Exception as e:
            logger.error(f"Error in worker completion callback: {e}")
            self._errors += 1
            
    def _finalize_scan(self):
        """Finalize scan when all workers complete"""
        try:
            elapsed_time = time.time() - self._scan_start_time
            
            # Send final progress update
            if self._progress_callback:
                final_progress = ScanProgress(
                    total_folders=self._total_folders,
                    scanned_folders=self._scanned_folders,
                    current_folder="Complete",
                    manga_found=self._manga_found,
                    errors=self._errors,
                    elapsed_time=elapsed_time,
                    estimated_remaining=0.0
                )
                self._progress_callback(final_progress)
            
            if self._cancel_requested:
                logger.info(
                    f"Scan cancelled: {self._manga_found} manga found, {self._errors} errors, "
                    f"{self._scanned_folders}/{self._total_folders} folders in {elapsed_time:.2f}s"
                )
            else:
                logger.success(f"All workers completed: {self._manga_found} manga found, {self._errors} errors in {elapsed_time:.2f}s")
            
            # Call completion callback if provided
            if self._completion_callback:
                try:
                    self._completion_callback(self._all_worker_results)
                except Exception as cb_error:
                    logger.error(f"Error in completion callback: {cb_error}")

            self._schedule_finalize_lifecycle()
            
        except Exception as e:
            logger.error(f"Error finalizing scan: {e}")
            # Call completion callback with error
            if self._completion_callback:
                try:
                    self._completion_callback([])
                except Exception as cb_error:
                    logger.error(f"Error in completion callback: {cb_error}")
            self._schedule_finalize_lifecycle()
    
    async def _scan_manga_folder_async(self, folder_path: Path) -> Optional[Manga]:
        """
        Asynchronous manga folder scanning that doesn't block the event loop
        
        Args:
            folder_path: Path to scan
            
        Returns:
            Manga object if valid structure found, None otherwise
        """
        try:
            from core.models import Chapter
            
            # Ensure folder_path is a Path object
            if isinstance(folder_path, str):
                folder_path = Path(folder_path)
            
            # Check if path exists
            if not folder_path.exists() or not folder_path.is_dir():
                return None
                
            # Scan for chapters asynchronously (non-blocking)
            chapters = []
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
            
            try:
                # Use asyncio.to_thread for I/O operations (Python 3.9+) or fall back to run_in_executor
                if hasattr(asyncio, 'to_thread'):
                    chapter_dirs = await asyncio.to_thread(list, folder_path.iterdir())
                else:
                    chapter_dirs = await asyncio.get_running_loop().run_in_executor(
                        None, list, folder_path.iterdir()
                    )
                
                # Process directories concurrently but with yield points
                for item in chapter_dirs:
                    # Yield control to event loop
                    await asyncio.sleep(0)
                    
                    if not item.is_dir():
                        continue
                    
                    # Check if directory contains images
                    image_files: List[Path] = []
                    
                    try:
                        # Get files in directory asynchronously
                        if hasattr(asyncio, 'to_thread'):
                            dir_files = await asyncio.to_thread(list, item.iterdir())
                        else:
                            dir_files = await asyncio.get_running_loop().run_in_executor(
                                None, list, item.iterdir()
                            )
                        
                        for img_file in dir_files:
                            # Yield control periodically
                            if len(image_files) % 50 == 0:
                                await asyncio.sleep(0)
                                
                            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                                image_files.append(img_file)
                        
                        # If we found images, it's a valid chapter
                        if image_files:
                            chapter = Chapter(
                                name=item.name,
                                path=item,
                                images=sorted(image_files, key=lambda p: p.name)
                            )
                            chapters.append(chapter)
                        
                    except (PermissionError, OSError) as e:
                        logger.debug(f"Could not scan chapter folder {item}: {e}")
                        continue
                
                # Only return manga if it has chapters
                if chapters:
                    # Sort chapters by name
                    chapters.sort(key=lambda c: c.name)
                    
                    # Create manga object
                    manga = Manga(
                        title=folder_path.name,
                        path=folder_path,
                        chapters=chapters
                    )
                    
                    # Try to find cover image asynchronously
                    manga.cover_url = await self._find_cover_image_async(folder_path)
                    return manga
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"Error scanning folder structure: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in async manga scan: {e}")
            return None
    
    async def _find_cover_image_async(self, manga_path: Path) -> str:
        """Find cover image for manga asynchronously"""
        try:
            # Look for common cover image names
            cover_names = ['cover', 'folder', 'thumb', 'thumbnail', '001', '01', '1']
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            for cover_name in cover_names:
                for ext in image_extensions:
                    cover_path = manga_path / f"{cover_name}{ext}"
                    # Yield control to event loop
                    await asyncio.sleep(0)
                    
                    if cover_path.exists():
                        return cover_path.as_uri()
            
            # If no specific cover found, use first image from first chapter
            if manga_path.exists():
                if hasattr(asyncio, 'to_thread'):
                    items = cast(
                        List[Path],
                        await asyncio.to_thread(sorted, manga_path.iterdir(), key=lambda p: p.name.lower()),
                    )
                else:
                    items = cast(List[Path], await asyncio.get_running_loop().run_in_executor(
                        None, lambda: sorted(manga_path.iterdir(), key=lambda p: p.name.lower())
                    ))
                
                for item in items:
                    await asyncio.sleep(0)  # Yield control
                    
                    if item.is_dir():
                        if hasattr(asyncio, 'to_thread'):
                            sub_items = cast(
                                List[Path],
                                await asyncio.to_thread(sorted, item.iterdir(), key=lambda p: p.name.lower()),
                            )
                        else:
                            sub_items = cast(List[Path], await asyncio.get_running_loop().run_in_executor(
                                None, lambda: sorted(item.iterdir(), key=lambda p: p.name.lower())
                            ))
                        
                        for img in sub_items:
                            if img.suffix.lower() in image_extensions:
                                return img.as_uri()
                        break
            
        except Exception as e:
            logger.debug(f"Error finding cover for {manga_path}: {e}")
        
        return ""
    
    async def _scan_single_folder(self, folder_path: Path, semaphore: asyncio.Semaphore) -> ScanResult:
        """
        Scan a single manga folder with intelligent caching
        
        Args:
            folder_path: Path to manga folder
            semaphore: Concurrency control semaphore
            
        Returns:
            ScanResult with manga or error information
        """
        async with semaphore:
            if self._cancel_requested:
                return ScanResult(
                    manga=None,
                    error="Scan cancelled",
                    path=folder_path
                )
            
            start_time = time.time()
            
            try:
                # Try cache first if enabled
                if self.cache_service and self.enable_cache:
                    cached_manga = self.cache_service.get_cached_manga(folder_path)
                    if cached_manga:
                        self._cache_hits += 1
                        scan_time = time.time() - start_time
                        cached_chapters_count = len(cached_manga.chapters or [])
                        logger.debug(f"Cache hit: {cached_manga.title} ({cached_chapters_count} chapters) in {scan_time:.3f}s")
                        return ScanResult(
                            manga=cached_manga,
                            scan_time=scan_time,
                            path=folder_path
                        )
                    else:
                        self._cache_misses += 1
                
                # Cache miss - perform actual scan
                loop = asyncio.get_running_loop()
                manga = await loop.run_in_executor(
                    self._executor,
                    self._scan_manga_folder_sync,
                    folder_path
                )
                
                scan_time = time.time() - start_time
                
                if manga:
                    # Cache the result if caching is enabled
                    if self.cache_service and self.enable_cache:
                        try:
                            self.cache_service.cache_manga(manga)
                        except Exception as cache_error:
                            logger.warning(f"Failed to cache manga {manga.title}: {cache_error}")
                    
                    scanned_chapters_count = len(manga.chapters or [])
                    logger.debug(f"Scanned manga: {manga.title} ({scanned_chapters_count} chapters) in {scan_time:.2f}s")
                    return ScanResult(
                        manga=manga,
                        scan_time=scan_time,
                        path=folder_path
                    )
                else:
                    return ScanResult(
                        manga=None,
                        error="No valid manga structure found",
                        scan_time=scan_time,
                        path=folder_path
                    )
                
            except Exception as e:
                scan_time = time.time() - start_time
                logger.error(f"Error scanning {folder_path}: {e}")
                return ScanResult(
                    manga=None,
                    error=str(e),
                    scan_time=scan_time,
                    path=folder_path
                )
    
    def _scan_manga_folder_sync(self, folder_path: Path) -> Optional[Manga]:
        """
        Synchronous manga folder scanning for thread execution
        
        Args:
            folder_path: Path to scan
            
        Returns:
            Manga object if valid structure found, None otherwise
        """
        try:
            from core.models import Chapter
            
            # Create manga object
            # Ensure folder_path is a Path object
            if isinstance(folder_path, str):
                folder_path = Path(folder_path)
                
            manga = Manga(
                title=folder_path.name,
                path=folder_path,
                chapters=[]
            )
            
            # Scan for chapters (subdirectories with images)
            chapters: List[Chapter] = []
            
            for item in folder_path.iterdir():
                if not item.is_dir():
                    continue
                
                # Check if directory contains images
                image_files: List[Path] = []
                image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
                
                try:
                    for img_file in item.iterdir():
                        if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                            image_files.append(img_file)
                
                    # If we found images, it's a valid chapter
                    if image_files:
                        chapter = Chapter(
                            name=item.name,
                            path=item,
                            images=sorted(image_files, key=lambda p: p.name)  # Sort for consistent ordering
                        )
                        chapters.append(chapter)
                    
                except (PermissionError, OSError) as e:
                    logger.debug(f"Could not scan chapter folder {item}: {e}")
                    continue
            
            # Sort chapters by name (natural sorting would be better but this works)
            chapters.sort(key=lambda c: c.name)
            manga.chapters = chapters
            
            # Only return manga if it has chapters
            if chapters:
                # Try to find cover image
                manga.cover_url = self._find_cover_image(folder_path)
                return manga
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in sync manga scan: {e}")
            return None
    
    def _find_cover_image(self, manga_path: Path) -> str:
        """Find cover image for manga"""
        try:
            # Look for common cover image names
            cover_names = ['cover', 'folder', 'thumb', 'thumbnail', '001', '01', '1']
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            for cover_name in cover_names:
                for ext in image_extensions:
                    cover_path = manga_path / f"{cover_name}{ext}"
                    if cover_path.exists():
                        return cover_path.as_uri()
            
            # If no specific cover found, use first image from first chapter
            if manga_path.exists():
                for item in sorted(manga_path.iterdir()):
                    if item.is_dir():
                        for img in sorted(item.iterdir()):
                            if img.suffix.lower() in image_extensions:
                                return img.as_uri()
                        break
            
        except Exception as e:
            logger.debug(f"Error finding cover for {manga_path}: {e}")
        
        return ""
    
    @property
    def is_scanning(self) -> bool:
        """Check if scan is currently in progress"""
        return self._is_scanning
    
    @property
    def scan_statistics(self) -> Dict[str, Any]:
        """Get current scan statistics including cache performance"""
        elapsed_time = time.time() - self._scan_start_time if self._scan_start_time > 0 else 0
        
        stats = {
            "is_scanning": self._is_scanning,
            "total_folders": self._total_folders,
            "scanned_folders": self._scanned_folders,
            "manga_found": self._manga_found,
            "errors": self._errors,
            "elapsed_time": elapsed_time,
            "scan_rate": self._scanned_folders / elapsed_time if elapsed_time > 0 else 0,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": (self._cache_hits / (self._cache_hits + self._cache_misses) * 100) if (self._cache_hits + self._cache_misses) > 0 else 0
        }
        
        # Add cache service statistics if available
        if self.cache_service:
            cache_stats = self.cache_service.get_statistics()
            stats.update({
                "cache_total_entries": cache_stats.entries_count,
                "cache_size_mb": cache_stats.total_size_mb,
                "cache_overall_hit_rate": cache_stats.hit_rate_percentage
            })
        
        return stats

    def get_worker_status(self) -> Dict[str, int]:
        """Get real-time worker counters for UI status displays."""
        total_workers = int(self._total_workers_count)
        completed_workers = int(self._completed_workers)
        active_workers = max(0, total_workers - completed_workers)
        return {
            "total_workers": total_workers,
            "active_workers": active_workers,
            "completed_workers": completed_workers,
        }
    
    def get_cache_statistics(self) -> Optional[Dict[str, Any]]:
        """Get detailed cache statistics"""
        if not self.cache_service:
            return None
        
        cache_stats = self.cache_service.get_statistics()
        return {
            "enabled": True,
            "total_requests": cache_stats.total_requests,
            "cache_hits": cache_stats.cache_hits,
            "cache_misses": cache_stats.cache_misses,
            "hit_rate_percentage": cache_stats.hit_rate_percentage,
            "entries_count": cache_stats.entries_count,
            "total_size_mb": cache_stats.total_size_mb,
            "oldest_entry_age_hours": cache_stats.oldest_entry_age / 3600
        }
    
    def clear_cache(self) -> bool:
        """Clear all cache entries"""
        if not self.cache_service:
            return False
        
        try:
            count = self.cache_service.clear_cache()
            logger.info(f"Cache cleared: {count} entries removed")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def optimize_cache(self) -> Optional[Dict[str, float]]:
        """Optimize cache by removing stale entries"""
        if not self.cache_service:
            return None
        
        try:
            return self.cache_service.optimize_cache()
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
            return None
    
    def _distribute_folders_evenly(self, folders: List[Path], num_workers: int) -> Dict[int, List[Path]]:
        """
        Distribute folders evenly across workers using round-robin algorithm.
        
        Args:
            folders: List of folder paths to distribute
            num_workers: Number of workers to distribute to
            
        Returns:
            Dictionary mapping worker_id to assigned folders
        """
        if num_workers <= 0:
            raise ValueError("Number of workers must be positive")
        
        if not folders:
            return {i: [] for i in range(1, num_workers + 1)}

        # Initialize worker assignments
        worker_assignments: Dict[int, List[Path]] = {i: [] for i in range(1, num_workers + 1)}
        
        # Balanced round-robin distribution
        for i, folder in enumerate(folders):
            worker_id = (i % num_workers) + 1
            worker_assignments[worker_id].append(folder)
        
        return worker_assignments
    
    async def _scan_worker_balanced(self, worker_id: int, folders: List[Path]) -> List[ScanResult]:
        """
        Worker function to scan assigned folders with balanced workload.
        
        Args:
            worker_id: Unique identifier for this worker
            folders: List of folders assigned to this worker
            
        Returns:
            List of ScanResult objects processed by this worker
        """
        import time
        
        worker_start_time = time.time()
        logger.info(f"Worker {worker_id} starting scan of {len(folders)} folders")
        
        results: List[ScanResult] = []
        
        try:
            # Process each assigned folder
            for folder_path in folders:
                if self._cancel_requested:
                    logger.info(f"Worker {worker_id} cancelled")
                    break
                
                # Ensure folder_path is a Path object
                if isinstance(folder_path, str):
                    folder_path = Path(folder_path)
                    
                try:
                    # Scan single folder (reuse existing method but without semaphore)
                    result = await self._scan_single_folder_direct(folder_path, worker_id)
                    results.append(result)
                    
                    # Send incremental result callback
                    if self._result_callback and result.success:
                        self._result_callback(result)
                        
                except Exception as e:
                    # Ensure folder_path is a Path object for .name access
                    folder_name = folder_path.name if isinstance(folder_path, Path) else Path(folder_path).name
                    logger.error(f"Worker {worker_id} failed to scan {folder_name}: {e}")
                    # Create failed result
                    failed_result = ScanResult(
                        path=folder_path,
                        error=str(e),
                        manga=None,
                        scan_time=0.0
                    )
                    results.append(failed_result)

            # Record worker statistics
            worker_duration = time.time() - worker_start_time
            folders_per_second = len(folders) / worker_duration if worker_duration > 0 else 0
            
            logger.info(
                f"Worker {worker_id} completed: {len([r for r in results if r.success])} successful scans "
                f"from {len(folders)} assigned folders in {worker_duration:.2f}s "
                f"({folders_per_second:.1f} folders/s)"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Worker {worker_id} encountered critical error: {e}")
            return results
    
    async def _scan_single_folder_direct(self, folder_path: Path, worker_id: int) -> ScanResult:
        """
        Scan a single folder directly without semaphore (for balanced workers).
        
        Args:
            folder_path: Path to the folder to scan
            worker_id: ID of the worker processing this folder
            
        Returns:
            ScanResult object
        """
        scan_start_time = time.time()
        
        try:
            # Ensure folder_path is a Path object
            if isinstance(folder_path, str):
                folder_path = Path(folder_path)
                
            # Ensure we can access .name safely
            folder_name = folder_path.name if isinstance(folder_path, Path) else Path(folder_path).name
            logger.debug(f"Worker {worker_id} scanning: {folder_name}")
            
            # Check cache first
            if self.cache_service:
                cached_manga = self.cache_service.get_cached_manga(folder_path)
                if cached_manga:
                    folder_name = folder_path.name if isinstance(folder_path, Path) else Path(folder_path).name
                    logger.debug(f"Worker {worker_id}: Cache hit for {folder_name}")
                    self._cache_hits += 1
                    
                    scan_time = time.time() - scan_start_time
                    return ScanResult(
                        path=folder_path,
                        manga=cached_manga,
                        scan_time=scan_time
                    )
                else:
                    self._cache_misses += 1
            
            # Scan manga folder asynchronously without blocking
            manga = await self._scan_manga_folder_async(folder_path)
            
            scan_time = time.time() - scan_start_time
            
            if manga:
                # Cache the result
                if self.cache_service:
                    self.cache_service.cache_manga(manga)
                
                worker_scanned_chapters = len(manga.chapters or [])
                logger.debug(f"Worker {worker_id}: Scanned {manga.title} ({worker_scanned_chapters} chapters) in {scan_time:.2f}s")
                
                return ScanResult(
                    path=folder_path,
                    manga=manga,
                    scan_time=scan_time
                )
            else:
                folder_name = folder_path.name if isinstance(folder_path, Path) else Path(folder_path).name
                logger.debug(f"Worker {worker_id}: No valid manga found in {folder_name}")
                return ScanResult(
                    path=folder_path,
                    error="No valid manga structure found",
                    manga=None,
                    scan_time=scan_time
                )
                
        except Exception as e:
            scan_time = time.time() - scan_start_time
            folder_name = folder_path.name if isinstance(folder_path, Path) else Path(folder_path).name
            logger.error(f"Worker {worker_id}: Error scanning {folder_name}: {e}")
            
            return ScanResult(
                path=folder_path,
                error=str(e),
                manga=None,
                scan_time=scan_time
            )