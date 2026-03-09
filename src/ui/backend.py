"""Refactored UI Backend - Orchestrates specialized handlers"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement, QJSValue
from pathlib import Path
import asyncio
import time
from typing import Any, List, Optional, cast

from core.config import ConfigManager
from core.services.uploader import MangaUploaderService
from core.services.queue import UploadQueue
from ui.models import GitHubFolderListModel
from ui.handlers import ConfigHandler, HostManager, MangaManager, GitHubManager
from loguru import logger

QML_IMPORT_NAME = "Backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Backend(QObject):
    """Main backend orchestrator using specialized handlers"""
    
    # Main signals
    processingStarted = Signal()
    processingFinished = Signal()
    error = Signal(str)
    progressChanged = Signal(float)
    metadataLoaded = Signal(dict)
    metadataUpdateCompleted = Signal()  # BULLETPROOF: Signal for GitHub button fix
    mangaInfoChanged = Signal()
    configChanged = Signal()
    mangaListChanged = Signal()
    chapterListChanged = Signal()
    libraryLoadingFinished = Signal()  # Signal when library loading is complete
    selectedHostIndexChanged = Signal()
    githubFoldersChanged = Signal()
    
    # Performance monitoring signals
    performanceChanged = Signal()
    scanProgressChanged = Signal(int)  # Progress percentage 0-100
    workerStatusChanged = Signal()
    
    # Folder dialog signals for QML integration
    openRootFolderDialog = Signal(str)  # Emits starting directory
    openOutputFolderDialog = Signal(str)  # Emits starting directory
    
    def __init__(self):
        super().__init__()
        
        # Core services
        self.config_manager = ConfigManager()
        self.uploader_service = MangaUploaderService()
        self.upload_queue = UploadQueue(max_concurrent=3)
        
        # Progressive scanning service
        from core.services.scan_service import ScanService
        from core.services.performance_service import PerformanceService
        from core.services.batch_service import BatchService
        self.scan_service = ScanService(max_workers=4)
        self.performance_service = PerformanceService(max_history_size=50)
        self.batch_service = BatchService(max_concurrent_jobs=2, max_concurrent_items=3)
        
        # Specialized handlers
        self.config_handler = ConfigHandler(self.config_manager)
        self.host_manager = HostManager(self.config_manager)
        self.manga_manager = MangaManager(self.config_manager, self.uploader_service)
        self.github_manager = GitHubManager(self.config_manager)
        
        # Scanning task tracking
        self._current_scan_task: Optional[asyncio.Task[Any]] = None
        self._background_tasks: set[asyncio.Task[Any]] = set()
        
        # Legacy models (TODO: migrate to handlers)
        self.github_folder_model = GitHubFolderListModel(self)
        
        # Internal state
        self._upload_progress = 0.0
        self._github_folders = ["metadata"]
        self._current_job_id = None
        self._current_upload_monitor_task: Optional[asyncio.Task[Any]] = None
        self._last_json_path = None
        self._upload_metadata = None
        self._manual_github_upload_in_progress = False
        self._processing_active = False
        self._is_shutting_down = False
        self._manga_info = {
            "title": "",
            "description": "",
            "artist": "",
            "author": "",
            "cover": "",
            "status": "",
            "group": "",
            "chapterCount": 0,
            "hasJson": False
        }
        self._last_logged_has_json: Optional[bool] = None
        
        # Performance monitoring state
        self._last_scan_time = "0.0s"
        self._active_workers = 0
        self._total_workers = 5
        self._cache_utilization = 0
        self._processing_queue = 0
        self._memory_usage = "0MB"
        self._scan_progress = 0
        
        # Batch processing state
        self._batch_queue_size = 0
        self._batch_active_jobs = 0
        
        # Start memory monitoring timer
        self._start_time = time.time()
        self._memory_timer = None
        
        # Connect handler signals to main signals
        self._connect_handler_signals()
        
        # Initialize services
        self._init_hosts()
        
        # CRITICAL: Initialize GitHub folders on startup if configured
        self._init_github_folders()
        
        # Initialize performance monitoring
        self._init_performance_monitoring()
        
        # Initialize batch service
        self._init_batch_service()
        
        logger.info("Backend initialized with specialized handlers, performance monitoring, and batch processing")

    def _emit_processing_started(self) -> None:
        """Emit processingStarted only on state transition."""
        if self._processing_active:
            return
        self._processing_active = True
        self.processingStarted.emit()

    def _emit_processing_finished(self) -> None:
        """Emit processingFinished only on state transition."""
        if not self._processing_active:
            return
        self._processing_active = False
        self.processingFinished.emit()

    def _on_background_task_done(self, task: asyncio.Task[Any]) -> None:
        """Handle completion of scheduled background tasks with explicit error logging."""
        self._background_tasks.discard(task)

        if task.cancelled():
            return

        try:
            task.result()
        except Exception as exc:
            logger.error(f"Background task failed: {exc}")

    def _schedule_task(self, coro: Any) -> Optional[asyncio.Task[Any]]:
        """Schedule coroutine on the active loop (running or startup-configured)."""
        if self._is_shutting_down:
            if asyncio.iscoroutine(coro):
                coro.close()
            logger.debug("Skipping background task scheduling because backend is shutting down")
            return None

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as exc:
                logger.error(f"Cannot schedule background task: {exc}")
                if asyncio.iscoroutine(coro):
                    coro.close()
                return None

            if loop.is_closed():
                logger.error("Cannot schedule background task: event loop is closed")
                if asyncio.iscoroutine(coro):
                    coro.close()
                return None

            logger.debug("Scheduling background task on configured event loop before run_forever")

        try:
            task = loop.create_task(coro)
        except RuntimeError as exc:
            logger.error(f"Cannot schedule background task: {exc}")
            if asyncio.iscoroutine(coro):
                coro.close()
            return None
        self._background_tasks.add(task)
        task.add_done_callback(self._on_background_task_done)
        return task
    
    def _connect_handler_signals(self):
        """Connect handler signals to main backend signals"""
        # Config handler signals
        self.config_handler.configChanged.connect(lambda: self.configChanged.emit())
        
        # Host manager signals  
        self.host_manager.hostChanged.connect(lambda: self.configChanged.emit())
        self.host_manager.hostChanged.connect(lambda: self.selectedHostIndexChanged.emit())
        self.host_manager.hostsInitialized.connect(self._on_hosts_initialized)
        
        # Manga manager signals - CRITICAL: Connect mangaInfoChanged signal
        self.manga_manager.mangaListChanged.connect(lambda: self.mangaListChanged.emit())
        self.manga_manager.chapterListChanged.connect(lambda: self.chapterListChanged.emit())
        self.manga_manager.mangaInfoChanged.connect(self._on_manga_info_changed)  # CRITICAL: Connect manga info changes
        self.manga_manager.uploadProgressChanged.connect(self._on_upload_progress)
        self.manga_manager.uploadCompleted.connect(self._on_upload_completed)
        self.manga_manager.uploadFailed.connect(self._on_upload_failed)
        
        # GitHub manager signals
        self.github_manager.githubConfigChanged.connect(lambda: self.configChanged.emit())
        self.github_manager.githubStatusChanged.connect(self._on_github_status_changed)
        # CRITICAL: Connect GitHub folder refresh to proper signal
        self.github_manager.githubFoldersChanged.connect(self._on_github_folders_updated)
    
    def _on_hosts_initialized(self):
        """Called when hosts are initialized"""
        logger.debug("Hosts initialization completed")
    
    def _on_upload_progress(self, manga_title: str, progress: int):
        """Handle upload progress updates"""
        normalized = float(progress)
        if normalized > 1.0:
            normalized = normalized / 100.0
        self._upload_progress = max(0.0, min(1.0, normalized))
        self.progressChanged.emit(self._upload_progress)
        logger.debug(f"Upload progress for {manga_title}: {progress}%")
    
    def _on_upload_completed(self, manga_title: str):
        """Handle upload completion"""
        self._emit_processing_finished()
        logger.info(f"Upload completed for: {manga_title}")
    
    def _on_upload_failed(self, manga_title: str, error_msg: str):
        """Handle upload failure"""
        self.error.emit(error_msg)
        self._emit_processing_finished()
        logger.error(f"Upload failed for {manga_title}: {error_msg}")
    
    def _on_github_status_changed(self, status: str):
        """Handle GitHub status changes"""
        logger.info(f"GitHub status: {status}")
    
    def _on_github_folders_updated(self, folders: List[str]):
        """Handle GitHub folder updates from GitHubManager - CRITICAL FIX"""
        try:
            # Update backend's folder list with data from GitHubManager
            self._github_folders = folders.copy()
            self.githubFoldersChanged.emit()
            logger.info(f"Updated GitHub folders in backend: {len(folders)} folders loaded: {folders[:5]}...")
        except Exception as e:
            logger.error(f"Error updating GitHub folders in backend: {e}")
    
    def _on_manga_info_changed(self, manga_info):
        """Handle manga info changes from MangaManager - CRITICAL FIXED FOR GITHUB BUTTON"""
        try:
            # Update internal manga info state with the comprehensive data from MangaManager
            if isinstance(manga_info, dict):
                self._manga_info.update(manga_info)
                logger.debug(f"Updated manga info from MangaManager: {manga_info.get('title', 'Unknown')} - hasJson: {manga_info.get('hasJson', False)}")
            else:
                # Handle QVariant from Qt signal
                if hasattr(manga_info, 'toVariant'):
                    manga_dict = manga_info.toVariant()
                else:
                    manga_dict = manga_info
                
                if isinstance(manga_dict, dict):
                    self._manga_info.update(manga_dict)
                    logger.debug(f"Updated manga info from QVariant: {manga_dict.get('title', 'Unknown')} - hasJson: {manga_dict.get('hasJson', False)}")
            
            # CRITICAL: Log the hasJson state for GitHub button troubleshooting
            has_json = self._manga_info.get('hasJson', False)
            title = self._manga_info.get('title', 'Unknown')
            logger.info(f"🔍 Backend manga info updated: {title} - hasJson={has_json} - GitHub button should be {'ENABLED' if has_json else 'DISABLED'}")
            
            # Emit signal to QML to update UI (including GitHub button state)
            self.mangaInfoChanged.emit()
            
        except Exception as e:
            logger.error(f"Error handling manga info change: {e}")
    
    # === DELEGATED PROPERTIES TO HANDLERS ===
    
    # Configuration Properties (delegated to ConfigHandler)
    @Property(str, notify=configChanged)
    def rootFolder(self):
        return self.config_handler.rootFolder
    
    @Property(str, notify=configChanged)
    def outputFolder(self):
        return self.config_handler.outputFolder
    
    @Property(str, notify=configChanged)
    def catboxUserhash(self):
        return self.config_handler.catboxUserhash
    
    @Property(str, notify=configChanged)
    def imgurClientId(self):
        return self.config_handler.imgurClientId
    
    @Property(str, notify=configChanged)
    def imgurAccessToken(self):
        return self.config_handler.imgurAccessToken
    
    @Property(str, notify=configChanged)
    def imgbbApiKey(self):
        return self.config_handler.imgbbApiKey
    
    @Property(str, notify=configChanged)
    def imageChestApiKey(self):
        return self.config_handler.imageChestApiKey
    
    @Property(str, notify=configChanged)
    def pixeldrainApiKey(self):
        return self.config_handler.pixeldrainApiKey
    
    @Property(str, notify=configChanged)
    def imgboxSessionCookie(self):
        return self.config_handler.imgboxSessionCookie
    
    @Property(str, notify=configChanged)
    def imghippoApiKey(self):
        return self.config_handler.imghippoApiKey
    
    @Property(str, notify=configChanged)
    def imgpileApiKey(self):
        return self.config_handler.imgpileApiKey
    
    @Property(str, notify=configChanged)
    def imgpileBaseUrl(self):
        return self.config_handler.imgpileBaseUrl
    
    @Property(int, notify=configChanged)
    def maxWorkers(self):
        return self.config_handler.maxWorkers
    
    @Property(float, notify=configChanged)
    def rateLimit(self):
        return self.config_handler.rateLimit
    
    # Host Properties (delegated to HostManager)
    @Property(list, constant=True)
    def availableHosts(self):
        return self.host_manager.hostsList
    
    @Property(str, notify=selectedHostIndexChanged)
    def selectedHost(self):
        return self.host_manager.selectedHost
    
    @Property(int, notify=selectedHostIndexChanged)
    def selectedHostIndex(self):
        return self.host_manager.selectedHostIndex
    
    @Property(bool, notify=configChanged)
    def isCatboxEnabled(self):
        return self.host_manager.isCatboxEnabled
    
    @Property(bool, notify=configChanged)
    def isImgurEnabled(self):
        return self.host_manager.isImgurEnabled
    
    @Property(bool, notify=configChanged)
    def isImgbbEnabled(self):
        return self.host_manager.isImgbbEnabled
    
    @Property(bool, notify=configChanged)
    def isImgboxEnabled(self):
        return self.host_manager.isImgboxEnabled
    
    @Property(bool, notify=configChanged)
    def isLensdumpEnabled(self):
        return self.host_manager.isLensdumpEnabled
    
    @Property(bool, notify=configChanged)
    def isPixeldrainEnabled(self):
        return self.host_manager.isPixeldrainEnabled
    
    @Property(bool, notify=configChanged)
    def isGofileEnabled(self):
        return self.host_manager.isGofileEnabled
    
    @Property(bool, notify=configChanged)
    def isImageChestEnabled(self):
        return self.host_manager.isImageChestEnabled
    
    @Property(bool, notify=configChanged)
    def isImgHippoEnabled(self):
        return self.host_manager.isImgHippoEnabled
    
    @Property(bool, notify=configChanged)
    def isImgPileEnabled(self):
        return self.host_manager.isImgPileEnabled
    
    # Manga Properties (delegated to MangaManager)
    @Property(QObject, notify=mangaListChanged)
    def mangaModel(self):
        return self.manga_manager.mangaModel
    
    @Property(QObject, notify=chapterListChanged)
    def chapterModel(self):
        return self.manga_manager.chapterModel
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaTitle(self):
        return self.manga_manager.selectedMangaTitle
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaCover(self):
        return self.manga_manager.selectedMangaCover
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaDescription(self):
        return self.manga_manager.selectedMangaDescription
    
    # GitHub Properties (delegated to GitHubManager)
    @Property(bool, notify=configChanged)
    def githubEnabled(self):
        return self.github_manager.githubEnabled
    
    @Property(str, notify=configChanged)
    def githubToken(self):
        return self.github_manager.githubToken
    
    @Property(str, notify=configChanged)
    def githubRepo(self):
        return self.github_manager.githubRepo
    
    @Property(str, notify=configChanged)
    def githubBranch(self):
        return self.github_manager.githubBranch
    
    @Property(str, notify=configChanged)
    def githubFolder(self):
        return self.github_manager.githubFolder
    
    @Property(bool, notify=configChanged)
    def githubAutoUpload(self):
        return self.github_manager.githubAutoUpload
    
    @Property(str, notify=configChanged)
    def githubCommitMessage(self):
        return self.github_manager.githubCommitMessage
    
    # JSON Update Mode Properties (delegated to ConfigHandler)
    @Property(str, notify=configChanged)
    def jsonUpdateMode(self):
        return self.config_handler.jsonUpdateMode
    
    @Property(list, constant=True)
    def availableUpdateModes(self):
        return self.config_handler.availableUpdateModes
    
    # Folder Structure Properties (delegated to ConfigHandler)
    @Property(str, notify=configChanged)
    def folderStructure(self):
        return self.config_handler.folderStructure
    
    @Property(list, constant=True)
    def availableFolderStructures(self):
        return self.config_handler.availableFolderStructures
    
    # Indexador Properties (delegated to GitHubManager)
    @Property(bool, notify=configChanged)
    def indexadorEnabled(self):
        return self.github_manager.indexadorEnabled
    
    @Property(str, notify=configChanged)
    def indexadorGroupName(self):
        return self.github_manager.indexadorGroupName
    
    @Property(str, notify=configChanged)
    def indexadorDescription(self):
        return self.github_manager.indexadorDescription
    
    @Property(str, notify=configChanged)
    def indexadorDiscord(self):
        return self.github_manager.indexadorDiscord
    
    @Property(str, notify=configChanged)
    def indexadorTelegram(self):
        return self.github_manager.indexadorTelegram
    
    @Property(str, notify=configChanged)
    def indexadorWebsite(self):
        return self.github_manager.indexadorWebsite
    
    @Property(str, notify=configChanged)
    def indexadorUrlTemplate(self):
        return self.github_manager.indexadorUrlTemplate
    
    # === PERFORMANCE MONITORING PROPERTIES ===
    
    @Property(str, notify=performanceChanged)
    def lastScanTime(self):
        """Last scan time in human readable format (e.g., '2.3s')"""
        return self._last_scan_time
    
    @Property(int, notify=workerStatusChanged)
    def activeWorkers(self):
        """Number of currently active workers"""
        return self._active_workers
    
    @Property(int, notify=workerStatusChanged)
    def totalWorkers(self):
        """Total number of configured workers"""
        return self._total_workers
    
    @Property(int, notify=performanceChanged)
    def cacheUtilization(self):
        """Cache hit rate percentage (0-100)"""
        return self._cache_utilization
    
    @Property(int, notify=performanceChanged)
    def processingQueue(self):
        """Number of items in processing queue"""
        return self._processing_queue
    
    @Property(str, notify=performanceChanged)
    def memoryUsage(self):
        """Current memory usage in human readable format (e.g., '245MB')"""
        self._update_memory_usage()
        return self._memory_usage
    
    @Property(int, notify=scanProgressChanged)
    def scanProgress(self):
        """Current scan progress percentage (0-100)"""
        return self._scan_progress
    
    @Property(int, notify=performanceChanged)
    def batchQueueSize(self):
        """Number of items in batch queue"""
        return self._batch_queue_size
    
    @Property(int, notify=performanceChanged) 
    def batchActiveJobs(self):
        """Number of active batch jobs"""
        return self._batch_active_jobs
    
    def _update_memory_usage(self):
        """Update current memory usage"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = int(process.memory_info().rss / 1024 / 1024)
            self._memory_usage = f"{memory_mb}MB"
        except ImportError:
            # Fallback if psutil not available
            import sys
            size = sys.getsizeof(self)
            self._memory_usage = f"{int(size / 1024 / 1024)}MB"
        except Exception as e:
            logger.warning(f"Could not get memory usage: {e}")
            self._memory_usage = "0MB"
    
    @Slot(str)
    def updateScanTime(self, scan_time: str):
        """Update the last scan time and emit signal"""
        if self._last_scan_time != scan_time:
            self._last_scan_time = scan_time
            self.performanceChanged.emit()
            logger.debug(f"Scan time updated: {scan_time}")
    
    @Slot(int, int)
    def updateWorkerStatus(self, active: int, total: int):
        """Update worker status and emit signal"""
        if self._active_workers != active or self._total_workers != total:
            self._active_workers = active
            self._total_workers = total
            self.workerStatusChanged.emit()
            logger.debug(f"Workers updated: {active}/{total}")
    
    @Slot(int)
    def updateCacheUtilization(self, utilization: int):
        """Update cache utilization percentage and emit signal"""
        if self._cache_utilization != utilization:
            self._cache_utilization = max(0, min(100, utilization))
            self.performanceChanged.emit()
            logger.debug(f"Cache utilization updated: {utilization}%")
    
    @Slot(int)
    def updateProcessingQueue(self, queue_size: int):
        """Update processing queue size and emit signal"""
        if self._processing_queue != queue_size:
            self._processing_queue = max(0, queue_size)
            self.performanceChanged.emit()
            logger.debug(f"Processing queue updated: {queue_size}")
    
    @Slot(int)
    def updateScanProgress(self, progress: int):
        """Update scan progress percentage and emit signal"""
        progress = max(0, min(100, progress))
        if self._scan_progress != progress:
            self._scan_progress = progress
            self.scanProgressChanged.emit(progress)
            logger.debug(f"Scan progress updated: {progress}%")
    
    # === CRITICAL MISSING METHODS FROM ORIGINAL ===
    
    @Slot()
    def _initialize_async_services_legacy(self):
        """Initialize async services after event loop is ready"""
        scheduled = self._schedule_task(self.upload_queue.start())
        if scheduled is None:
            logger.debug("Legacy async service init skipped (event loop unavailable)")
    
    @Slot()
    def _loadConfig_legacy(self):
        """Load configuration on startup"""
        self.config_manager.config = self.config_manager.load_config()
        self.configChanged.emit()
    
    @Slot()
    def _saveConfig_legacy(self):
        """Save current configuration"""
        self.config_manager.save_config()
        self.configChanged.emit()
    
    @Slot('QVariant')
    def updateConfig(self, config_data):
        """Update configuration from QML - CRITICAL METHOD"""
        try:
            logger.debug(f"updateConfig received: {type(config_data)}")
            
            # Convert QJSValue to Python dict if needed - EXACTLY like original
            if isinstance(config_data, QJSValue):
                config_dict = config_data.toVariant()
                logger.debug(f"Converted QJSValue to: {type(config_dict)}")
            elif hasattr(config_data, 'toVariant'):
                config_dict = config_data.toVariant()
                logger.debug(f"Converted to variant: {type(config_dict)}")
            else:
                config_dict = config_data
                logger.debug(f"Using direct type: {type(config_dict)}")
            
            # Ensure we have a valid dict - CRITICAL validation
            if not isinstance(config_dict, dict):
                error_msg = f"Dados de configuração inválidos: {type(config_dict)}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
                
            logger.debug(f"Config dict keys: {list(config_dict.keys())}")
            
            # Update paths - CRITICAL for QML folder dialogs
            if "rootFolder" in config_dict:
                root_path_str = self._clean_file_url(config_dict["rootFolder"])
                if root_path_str:
                    self.config_manager.config.root_folder = Path(root_path_str)
                    logger.debug(f"Updated root folder: {self.config_manager.config.root_folder}")
            
            if "outputFolder" in config_dict:
                output_path_str = self._clean_file_url(config_dict["outputFolder"])
                if output_path_str:
                    self.config_manager.config.output_folder = Path(output_path_str)
                else:
                    self.config_manager.config.output_folder = (
                        self.config_manager.config.root_folder / "Manga_Metadata_Output"
                    )
                logger.debug(f"Updated output folder: {self.config_manager.config.output_folder}")
            
            # Update host configurations - CRITICAL
            self._update_host_configs(config_dict)
            
            # Update GitHub settings - CRITICAL FOR GITHUB FUNCTIONALITY
            github_config_keys = [
                "githubToken", "githubRepo", "githubBranch", "githubFolder", 
                "githubAutoUpload", "githubCommitMessage", "githubEnabled"
            ]
            github_config_updated = any(key in config_dict for key in github_config_keys)
            
            if github_config_updated:
                try:
                    self.github_manager.update_github_config(config_dict)
                    logger.debug("Updated GitHub configuration")
                except Exception as e:
                    logger.error(f"Error updating GitHub config: {e}")
            
            # Update other settings
            if "jsonUpdateMode" in config_dict:
                self.config_manager.config.json_update_mode = str(config_dict["jsonUpdateMode"]).strip()
            
            # Update folder structure
            if "folderStructure" in config_dict:
                structure = str(config_dict["folderStructure"]).strip()
                if structure in ["standard", "flat", "volume_based", "scan_manga_chapter", "scan_manga_volume_chapter"]:
                    self.config_manager.config.folder_structure = structure
                    logger.debug(f"Updated folder structure: {structure}")
            
            # Update selected host - CRITICAL
            if "selectedHost" in config_dict:
                selected_host = str(config_dict["selectedHost"]).strip()
                if selected_host and selected_host in self.host_manager.host_list:
                    self.config_manager.config.selected_host = selected_host
                    self.host_manager.set_host(selected_host)
                    logger.debug(f"Updated selected host: {selected_host}")
            
            # Save configuration and emit signals
            self.config_manager.save_config()
            self.configChanged.emit()
            
            # Emit host change signal if needed
            if "selectedHost" in config_dict:
                self.selectedHostIndexChanged.emit()
            
            # Reload hosts if configuration changed (especially after host config updates)
            host_config_keys = [
                "catboxUserhash", "imgurClientId", "imgurAccessToken", 
                "imgbbApiKey", "imageChestApiKey", "pixeldrainApiKey", 
                "imgboxSessionCookie", "imghippoApiKey", "imgpileApiKey", "imgpileBaseUrl"
            ]
            if any(key in config_dict for key in host_config_keys):
                # Reload hosts asynchronously to prevent UI blocking
                task = self._schedule_task(self._reload_hosts_async())
                if task is None:
                    logger.warning("Could not schedule async host reload after configuration change")
                else:
                    logger.debug("Started async host reload after configuration change")
            
            # Refresh manga list if folder paths changed (asynchronously)
            if "rootFolder" in config_dict or "outputFolder" in config_dict:
                task = self._schedule_task(self._refresh_manga_list_async())
                if task is None:
                    logger.warning("Could not schedule async manga list refresh after folder path change")
                else:
                    logger.debug("Started async manga list refresh after folder path change")
            
        except Exception as e:
            error_msg = f"Erro ao salvar configuração: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Config data type was: {type(config_data)}")
            if hasattr(config_data, '__dict__'):
                logger.error(f"Config data dict: {config_data.__dict__}")
            self.error.emit(error_msg)
    
    def _clean_file_url(self, path_str: str) -> str:
        """Clean file:// URLs from QML FolderDialog - CRITICAL for path handling"""
        path_str = str(path_str).strip()
        if path_str.startswith("file:///"):
            path_str = path_str[8:]
        elif path_str.startswith("file://"):
            path_str = path_str[7:]
        
        if path_str and not path_str.startswith('/'):
            path_str = '/' + path_str
        
        return path_str
    
    def _update_host_configs(self, config_dict: dict):
        """Update host-specific configurations - CRITICAL"""
        host_configs = {
            "catboxUserhash": ("Catbox", "userhash"),
            "imgurClientId": ("Imgur", "client_id"),
            "imgurAccessToken": ("Imgur", "access_token"),
            "imgbbApiKey": ("ImgBB", "api_key"),
            "imageChestApiKey": ("ImageChest", "api_key"),
            "pixeldrainApiKey": ("Pixeldrain", "api_key"),
            "imgboxSessionCookie": ("Imgbox", "session_cookie"),
            "imghippoApiKey": ("ImgHippo", "api_key"),
            "imgpileApiKey": ("ImgPile", "api_key"),
            "imgpileBaseUrl": ("ImgPile", "base_url"),
        }
        
        for config_key, (host_name, attr_name) in host_configs.items():
            if config_key in config_dict:
                host_config = self.config_manager.config.hosts.get(host_name)
                if host_config:
                    setattr(host_config, attr_name, config_dict[config_key])
                    # Enable host if API key provided
                    if config_key in ["imgurClientId", "imgbbApiKey", "imageChestApiKey"]:
                        host_config.enabled = bool(config_dict[config_key])
                    elif config_key == "pixeldrainApiKey":
                        host_config.enabled = True  # Pixeldrain works without API key
                    elif config_key == "imgboxSessionCookie":
                        host_config.enabled = True
        
        # Update worker settings for current host
        if "maxWorkers" in config_dict or "rateLimit" in config_dict:
            current_host = self.config_manager.config.selected_host
            host_config = self.config_manager.config.hosts.get(current_host)
            if host_config:
                if "maxWorkers" in config_dict:
                    host_config.max_workers = config_dict["maxWorkers"]
                if "rateLimit" in config_dict:
                    host_config.rate_limit = float(config_dict["rateLimit"])
    
    @Slot(str)
    def setHost(self, host_name: str):
        """Set active host (delegated to HostManager)"""
        self.host_manager.set_host(host_name)
        
    # === CRITICAL MISSING SLOTS FROM ORIGINAL ===
    
    @Slot(str)
    def _filterMangaList_legacy(self, search_text: str):
        """Filter manga list based on search text - CRITICAL"""
        self.manga_manager.filter_manga_list(search_text)
    
    @Slot(str)
    def _loadMangaDetails_legacy(self, manga_path: str):
        """Load details for specific manga - CRITICAL"""
        try:
            # Delegate to MangaManager which handles comprehensive metadata loading
            self.manga_manager.load_manga_details(manga_path)
            logger.debug(f"Loaded manga details for: {manga_path}")
        except Exception as e:
            error_msg = f"Erro ao carregar detalhes do manga: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(str)
    def setImgHippoApiKey(self, api_key: str):
        """Set ImgHippo API key - CRITICAL for host config"""
        host_config = self.config_manager.config.hosts.get("ImgHippo")
        if host_config:
            host_config.api_key = api_key
            host_config.enabled = bool(api_key)
            self.config_manager.save_config()
            self.configChanged.emit()
    
    @Slot(str)
    def setImgPileApiKey(self, api_key: str):
        """Set ImgPile API key - CRITICAL for host config"""
        host_config = self.config_manager.config.hosts.get("ImgPile")
        if host_config:
            host_config.api_key = api_key
            host_config.enabled = bool(api_key)
            self.config_manager.save_config()
            self.configChanged.emit()
    
    @Slot(str)
    def setImgPileBaseUrl(self, base_url: str):
        """Set ImgPile base URL - CRITICAL for custom instances"""
        host_config = self.config_manager.config.hosts.get("ImgPile")
        if host_config:
            host_config.base_url = base_url or "https://imgpile.com"
            self.config_manager.save_config()
            self.configChanged.emit()
    
    @Slot()
    def _startUpload_legacy(self):
        """Start upload process - CRITICAL"""
        try:
            # Keep legacy entrypoint aligned with the real queued upload flow.
            self.startUpload()
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot('QVariant')
    def _startUploadWithMetadata_legacy(self, metadata):
        """Start upload with custom metadata - CRITICAL"""
        try:
            # Store metadata for upload
            self._upload_metadata = metadata
            self.startUpload()
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload com metadata: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot()
    def saveToGitHub(self):
        """Save metadata to GitHub - COMPREHENSIVE FIXED VERSION WITH ENHANCED LOGGING"""
        try:
            if self._manual_github_upload_in_progress:
                self.error.emit("Upload do GitHub já está em andamento")
                return

            # CRITICAL: Log the GitHub button state for debugging
            has_json = self._manga_info.get('hasJson', False)
            current_title = self._manga_info.get('title', 'None')
            logger.info(f"🚀 GitHub button clicked - Current manga: {current_title} - hasJson: {has_json}")
            
            # Check GitHub configuration first
            if not self.github_manager.is_github_configured():
                error_msg = "Configurações do GitHub incompletas. Verifique token e repositório."
                logger.warning(error_msg)
                self.error.emit(error_msg)
                return
            
            # Get output folder for JSON search
            output_folder = self.config_manager.config.output_folder
            if not output_folder.exists():
                error_msg = f"Pasta de saída não existe: {output_folder}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            # Enhanced JSON file detection logic
            json_file = self._find_json_file_for_upload(output_folder)
            
            if not json_file:
                error_msg = "Nenhum arquivo de metadados encontrado. Execute um upload primeiro para gerar metadados."
                logger.warning(error_msg)
                self.error.emit(error_msg)
                return
            
            logger.info(f"✅ Preparando upload do GitHub para: {json_file}")

            # Keep UI processing state consistent for manual GitHub uploads.
            self._manual_github_upload_in_progress = True
            self._emit_processing_started()
            
            # Start GitHub upload with better error handling
            task = self._schedule_task(self._upload_to_github_safe(json_file))
            if task is None:
                self.error.emit("Erro ao agendar upload para GitHub")
                self._manual_github_upload_in_progress = False
                self._emit_processing_finished()
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload do GitHub: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
            if self._manual_github_upload_in_progress:
                self._manual_github_upload_in_progress = False
                self._emit_processing_finished()
    
    def _find_json_file_for_upload(self, output_folder: Path) -> Optional[Path]:
        """Find JSON file for GitHub upload using multiple strategies"""
        try:
            from utils.helpers import sanitize_filename
            
            # Strategy 1: If manga is selected, look in its specific folder
            if self.manga_manager.current_manga:
                manga_title = self.manga_manager.current_manga.title
                logger.debug(f"Looking for JSON for selected manga: {manga_title}")
                
                # Check in manga-specific folder
                manga_folder = output_folder / manga_title
                if manga_folder.exists():
                    # Try sanitized filename
                    sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
                    json_file_path = manga_folder / f"{sanitized_title}.json"
                    if json_file_path.exists():
                        logger.debug(f"Found JSON file: {json_file_path}")
                        return cast(Path, json_file_path)
                    
                    # Try any JSON in manga folder
                    for file in manga_folder.glob("*.json"):
                        logger.debug(f"Found JSON file: {file}")
                        return cast(Path, file)
                
                # Strategy 1.5: Similar folder matching
                manga_name_words = set(manga_title.lower().split())
                for folder in output_folder.iterdir():
                    if folder.is_dir():
                        folder_name_words = set(folder.name.lower().split())
                        if len(manga_name_words & folder_name_words) >= 2:
                            for file in folder.glob("*.json"):
                                logger.debug(f"Found JSON file in similar folder: {file}")
                                return file
                
                # Strategy 2: Search by title in output folder
                for file in output_folder.glob("*.json"):
                    if manga_title.lower() in file.stem.lower():
                        logger.debug(f"Found JSON file by title match: {file}")
                        return file
            
            # Strategy 3: If no manga selected or no specific match, find any recent JSON
            logger.debug("Searching for any recent JSON files in output folder")
            json_files = list(output_folder.glob("**/*.json"))
            
            if json_files:
                # Sort by modification time, newest first
                json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                logger.debug(f"Found {len(json_files)} JSON files, using most recent: {json_files[0]}")
                return json_files[0]
            
            logger.warning(f"No JSON files found in output folder: {output_folder}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding JSON file: {e}")
            return None
    
    async def _upload_to_github_safe(self, json_file: Path):
        """Safe wrapper for GitHub upload with proper error handling"""
        try:
            # Notify start of upload process
            logger.info(f"Iniciando upload do GitHub: {json_file.name}")
            
            # Call the original upload method
            await self._upload_to_github(json_file)
            
        except Exception as e:
            error_msg = f"Erro durante upload do GitHub: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
        finally:
            self._manual_github_upload_in_progress = False
            self._emit_processing_finished()
    
    @Slot()
    def refreshGitHubFolders(self):
        """Refresh GitHub folders - CRITICAL - Delegate to GitHubManager"""
        try:
            # CRITICAL: Use GitHubManager's method which now properly emits signals
            self.github_manager.refreshGitHubFolders()
            logger.debug("Delegated GitHub folders refresh to GitHubManager")
            
        except Exception as e:
            logger.error(f"Error refreshing GitHub folders: {e}")
            self.error.emit(f"Erro ao carregar pastas do GitHub: {str(e)}")
    
    @Slot(str)
    def _selectGitHubFolder_legacy(self, folder_path: str):
        """Select GitHub folder - CRITICAL"""
        self.github_manager.select_folder(folder_path)
    
    @Slot(str, result=str)
    def _makeJsonSafe_legacy(self, text: str) -> str:
        """Make text safe for JSON - CRITICAL utility"""
        if not text:
            return ""
        
        # Replace problematic characters
        safe_text = text.replace('"', '\\"')
        safe_text = safe_text.replace('\n', '\\n')
        safe_text = safe_text.replace('\r', '\\r')
        safe_text = safe_text.replace('\t', '\\t')
        
        return safe_text
    
    @Slot(str)
    def loadExistingMetadata(self, manga_title: str):
        """Load existing metadata for manga - CRITICAL"""
        try:
            logger.debug(f"Loading existing metadata for: {manga_title}")
            
            # Use MangaManager's comprehensive metadata loading method
            metadata = self.manga_manager.load_existing_metadata(manga_title)
            
            if metadata:
                # Ensure all required fields are present
                complete_metadata = {
                    "title": metadata.get("title", manga_title),
                    "description": metadata.get("description", ""),
                    "artist": metadata.get("artist", ""),
                    "author": metadata.get("author", ""),
                    "group": metadata.get("group", ""),
                    "cover": metadata.get("cover", ""),
                    "status": metadata.get("status", "Em Andamento"),
                    "_requestMangaTitle": manga_title,
                }
                
                # Update internal state
                self._manga_info.update(complete_metadata)
                
                # Emit signal with loaded metadata for QML
                self.metadataLoaded.emit(complete_metadata)
                logger.debug(f"Emitted metadata for {manga_title}: artist='{complete_metadata['artist']}', "
                           f"author='{complete_metadata['author']}', group='{complete_metadata['group']}'")
            else:
                # No metadata found, emit default
                default_metadata = {
                    "title": manga_title,
                    "description": "",
                    "artist": "",
                    "author": "",
                    "group": "",
                    "cover": "",
                    "status": "Em Andamento",
                    "_requestMangaTitle": manga_title,
                }
                self.metadataLoaded.emit(default_metadata)
                logger.debug(f"No metadata found for {manga_title}, using defaults")
            
        except Exception as e:
            error_msg = f"Erro ao carregar metadata: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot('QVariant')
    def _updateExistingMetadata_legacy(self, metadata):
        """Update existing metadata - CRITICAL FIXED FOR GITHUB BUTTON STATE"""
        try:
            # Convert QJSValue to dict if needed
            if isinstance(metadata, QJSValue):
                metadata_dict = metadata.toVariant()
                logger.debug(f"Converted QJSValue to: {type(metadata_dict)}")
            elif hasattr(metadata, 'toVariant'):
                metadata_dict = metadata.toVariant()
                logger.debug(f"Converted to variant: {type(metadata_dict)}")
            else:
                metadata_dict = metadata
                logger.debug(f"Using direct type: {type(metadata_dict)}")
            
            # Ensure we have a valid dict
            if not isinstance(metadata_dict, dict):
                error_msg = f"Dados de metadados inválidos: {type(metadata_dict)}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            # Fix escaped newlines in description from QML
            if 'description' in metadata_dict and isinstance(metadata_dict['description'], str):
                # Fix escaped newlines: \\n -> \n
                original_desc = metadata_dict['description']
                metadata_dict['description'] = original_desc.replace('\\n', '\n')
                if original_desc != metadata_dict['description']:
                    logger.debug("Fixed escaped newlines in description")
            
            logger.info(f"📝 Starting metadata update for: {metadata_dict.get('title', 'Unknown')}")
            
            # Delegate to MangaManager for comprehensive metadata update
            # CRITICAL: This will automatically emit mangaInfoChanged signal with hasJson=true
            self.manga_manager.update_metadata(metadata_dict)
            
            # NOTE: We don't manually update _manga_info here anymore because
            # MangaManager.update_metadata() will emit mangaInfoChanged signal
            # which will be handled by _on_manga_info_changed() and properly
            # update the state including hasJson=true
            
            # BULLETPROOF: Emit signal to force GitHub button refresh
            self.metadataUpdateCompleted.emit()
            
            logger.info(f"✅ Metadata update completed for: {metadata_dict.get('title', 'Unknown')}")
            
        except Exception as e:
            error_msg = f"Erro ao atualizar metadata: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(str)
    def _testImgboxCookie_legacy(self, cookie):
        """Test Imgbox cookie validity - CRITICAL"""
        try:
            # Delegate to host manager for cookie testing
            self.host_manager.test_imgbox_cookie(cookie)
            
        except Exception as e:
            error_msg = f"Erro ao testar cookie: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot()
    def refreshMangaList(self):
        """Refresh manga list asynchronously (delegated to MangaManager)"""
        task = self._schedule_task(self._refresh_manga_list_async())
        if task is None:
            self.error.emit("Erro ao agendar recarregamento da biblioteca")
            self.libraryLoadingFinished.emit()
    
    async def _refresh_manga_list_async(self):
        """Async version of refresh manga list"""
        try:
            # Qt models/signals must be updated on the main thread.
            self.manga_manager.refresh_manga_list()
            await asyncio.sleep(0)
            # Emit signal when finished
            self.libraryLoadingFinished.emit()
        except Exception as e:
            logger.error(f"Error refreshing manga list: {e}")
            self.error.emit(f"Erro ao carregar biblioteca: {str(e)}")
            self.libraryLoadingFinished.emit()  # Still emit signal even on error
    
    @Slot(result=bool)
    def startProgressiveScan(self):
        """Start progressive library scanning with real-time updates"""
        try:
            if self._is_shutting_down:
                logger.debug("Ignoring progressive scan request during backend shutdown")
                return False

            if self.scan_service.is_scanning:
                logger.debug("Ignoring progressive scan request because a scan is already in progress")
                return False

            root_folder = Path(self.config_manager.config.root_folder)
            if not root_folder.exists():
                self.error.emit(f"Pasta raiz não existe: {root_folder}")
                self.updateScanProgress(0)
                self.libraryLoadingFinished.emit()
                return False
            
            logger.info(f"Starting progressive library scan: {root_folder}")
            
            # Update worker count from current configuration
            current_host = self.config_manager.config.selected_host
            host_config = self.config_manager.config.hosts.get(current_host)
            if host_config:
                max_workers = getattr(host_config, 'max_workers', 4)
                self.scan_service.max_workers = max_workers
                self.updateWorkerStatus(0, max_workers)
            
            # Reset scan progress
            self.updateScanProgress(0)
            
            # Start async scan
            task = self._schedule_task(self._progressive_scan_async(root_folder))
            if task is None:
                self.error.emit("Erro ao agendar varredura progressiva")
                self.libraryLoadingFinished.emit()
                return False

            return True
            
        except Exception as e:
            error_msg = f"Erro ao iniciar varredura progressiva: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
            self.libraryLoadingFinished.emit()
            return False
    
    @Slot()
    def cancelProgressiveScan(self):
        """Cancel the current progressive scan"""
        try:
            if self.scan_service.is_scanning:
                logger.info("Cancelling progressive scan...")
                cancel_task = self._schedule_task(self.scan_service.cancel_scan())
                if cancel_task is None:
                    self.error.emit("Erro ao cancelar varredura progressiva")
                
                # Cancel the background task if it exists
                if self._current_scan_task and not self._current_scan_task.done():
                    self._current_scan_task.cancel()
                    self._current_scan_task = None
                    
                self.updateScanProgress(0)
                self.updateWorkerStatus(0, self._total_workers)
            else:
                logger.debug("No scan in progress to cancel")
        except Exception as e:
            logger.error(f"Error cancelling scan: {e}")
    
    async def _progressive_scan_async(self, root_path: Path):
        """Async progressive scan with real-time updates"""
        scan_start_time = time.time()
        
        try:
            # Progress callback for real-time updates
            def on_progress(progress):
                try:
                    # Update scan progress
                    self.updateScanProgress(progress.progress_percentage)

                    # Update worker status using actual counters from ScanService.
                    worker_status = self.scan_service.get_worker_status()
                    total_workers = worker_status.get("total_workers", 0)
                    active_workers = worker_status.get("active_workers", 0)
                    if total_workers <= 0:
                        total_workers = self.scan_service.max_workers
                    self.updateWorkerStatus(active_workers, total_workers)
                    
                    # Update performance time
                    self.updateScanTime(f"{progress.elapsed_time:.1f}s")
                    
                    logger.debug(f"Scan progress: {progress.progress_percentage}% - "
                               f"{progress.manga_found} manga found, "
                               f"{progress.errors} errors, "
                               f"Rate: {progress.scan_rate:.1f} folders/s")
                    
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
            
            # Result callback for incremental manga updates
            def on_result(result):
                try:
                    if result.success and result.manga:
                        # Add manga to the manga manager incrementally
                        self.manga_manager.add_manga_incremental(result.manga)
                        
                        logger.debug(f"Added manga incrementally: {result.manga.title} "
                                   f"({len(result.manga.chapters)} chapters)")
                    
                except Exception as e:
                    logger.error(f"Error in result callback: {e}")
            
            # Completion callback for when all workers finish
            def on_completion(results):
                try:
                    # This will be called when all workers actually complete
                    logger.info(f"Scan completion callback: {len(results)} total results")
                    self._handle_scan_completion(results)
                except Exception as e:
                    logger.error(f"Error in completion callback: {e}")
            
            # Start the progressive scan in background (non-blocking)
            scan_task = self._schedule_task(
                self.scan_service.start_scan(
                    root_path=root_path,
                    progress_callback=on_progress,
                    result_callback=on_result,
                    completion_callback=on_completion
                )
            )

            if scan_task is None:
                self.error.emit("Erro ao iniciar varredura progressiva (loop indisponivel)")
                self.libraryLoadingFinished.emit()
                return
            
            # Store task reference to prevent garbage collection
            self._current_scan_task = scan_task
            
            # Don't set up completion callback on task - we use the custom completion callback
            logger.info("Progressive scan started in background - UI remains responsive")
            return
            
        except Exception as e:
            elapsed_time = time.time() - scan_start_time
            error_msg = f"Erro durante varredura progressiva: {str(e)}"
            logger.error(error_msg)
            
            # Reset status
            self.updateScanTime(f"{elapsed_time:.1f}s")
            self.updateScanProgress(0)
            self.updateWorkerStatus(0, self._total_workers)
            
            self.error.emit(error_msg)
            self.libraryLoadingFinished.emit()
    
    def _handle_scan_completion(self, results):
        """Handle scan completion when all workers finish"""
        try:
            # Results are already provided as parameter
            logger.debug(f"Handling completion for {len(results)} scan results")
            
            # Update cache utilization from scan statistics
            if self.scan_service.cache_service:
                cache_stats = self.scan_service.get_cache_statistics()
                if cache_stats:
                    # Update cache utilization based on hit rate
                    self.updateCacheUtilization(int(cache_stats["hit_rate_percentage"]))
                    logger.debug(f"Cache performance: {cache_stats['hit_rate_percentage']:.1f}% hit rate, "
                               f"{cache_stats['entries_count']} entries, {cache_stats['total_size_mb']:.1f} MB")
            
            # Final updates
            manga_count = sum(1 for r in results if r.success)
            error_count = sum(1 for r in results if not r.success)
            total_files = sum(r.manga.chapters and sum(len(ch.images or []) for ch in r.manga.chapters) or 0 
                             for r in results if r.success and r.manga and r.manga.chapters)
            
            # Get scan statistics for performance recording
            scan_stats = self.scan_service.scan_statistics
            elapsed_time = scan_stats["elapsed_time"]
            total_folders = int(scan_stats.get("total_folders", 0))
            scanned_folders = int(scan_stats.get("scanned_folders", 0))
            
            # Record performance metrics
            cache_hit_rate = 0
            if self.scan_service.cache_service:
                cache_stats = self.scan_service.get_cache_statistics()
                cache_hit_rate = cache_stats["hit_rate_percentage"] if cache_stats else 0
            
            # Record in performance service
            performance_metric = self.performance_service.record_scan_performance(
                scan_time=elapsed_time,
                folder_count=len(results),
                file_count=total_files,
                cache_hit_rate=cache_hit_rate,
                worker_count=self._total_workers
            )
            
            self.updateScanTime(f"{elapsed_time:.1f}s")
            if total_folders > 0:
                final_progress = int(min(100, (scanned_folders / total_folders) * 100))
            else:
                final_progress = 100
            self.updateScanProgress(final_progress)
            self.updateWorkerStatus(0, self._total_workers)  # No workers active after completion
            
            # Update performance grade in UI
            if performance_metric:
                logger.info(f"Performance grade: {performance_metric.performance_grade} "
                           f"(scan rate: {performance_metric.scan_rate:.1f} folders/s)")
            
            # Emit completion signal
            self.libraryLoadingFinished.emit()
            
            cancelled = total_folders > 0 and scanned_folders < total_folders
            if cancelled:
                logger.info(
                    f"Progressive scan interrupted: {manga_count} manga loaded, "
                    f"{error_count} errors, {scanned_folders}/{total_folders} folders in {elapsed_time:.2f}s"
                )
            else:
                logger.success(f"Progressive scan completed: {manga_count} manga loaded, "
                             f"{error_count} errors in {elapsed_time:.2f}s")
            
            # Clear task reference
            self._current_scan_task = None
            
        except Exception as e:
            logger.error(f"Error in scan completion callback: {e}")
            self.updateScanProgress(0)
            self.updateWorkerStatus(0, self._total_workers)
            self.error.emit(f"Erro ao finalizar varredura: {str(e)}")
            self.libraryLoadingFinished.emit()
            self._current_scan_task = None
    
    @Slot()
    def clearCache(self):
        """Clear manga scanning cache"""
        try:
            if self.scan_service.clear_cache():
                self.updateCacheUtilization(0)
                logger.info("Cache cleared successfully")
            else:
                logger.warning("Cache service not available")
        except Exception as e:
            error_msg = f"Erro ao limpar cache: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot()
    def optimizeCache(self):
        """Optimize cache by removing stale entries"""
        try:
            results = self.scan_service.optimize_cache()
            if results:
                logger.info(f"Cache optimized: removed {results.get('stale_removed', 0) + results.get('invalid_removed', 0)} entries")
                # Update cache utilization
                cache_stats = self.scan_service.get_cache_statistics()
                if cache_stats:
                    self.updateCacheUtilization(int(cache_stats["hit_rate_percentage"]))
            else:
                logger.warning("Cache service not available")
        except Exception as e:
            error_msg = f"Erro ao otimizar cache: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(result='QVariant')
    def getCacheStatistics(self):
        """Get detailed cache statistics for QML"""
        try:
            cache_stats = self.scan_service.get_cache_statistics()
            if cache_stats:
                return {
                    "enabled": True,
                    "hitRate": cache_stats["hit_rate_percentage"],
                    "totalEntries": cache_stats["entries_count"],
                    "sizeMB": cache_stats["total_size_mb"],
                    "oldestEntryHours": cache_stats["oldest_entry_age_hours"]
                }
            else:
                return {"enabled": False}
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {"enabled": False, "error": str(e)}
    
    @Slot(result=str)
    def getPerformanceGrade(self):
        """Get current performance grade for QML"""
        try:
            return self.performance_service.get_current_performance_grade()
        except Exception as e:
            logger.error(f"Error getting performance grade: {e}")
            return "N/A"
    
    @Slot(result='QVariant')
    def getPerformanceSummary(self):
        """Get performance summary for QML"""
        try:
            summary = self.performance_service.get_performance_summary()
            return {
                "grade": summary.get("current_grade", "N/A"),
                "scanRate": summary.get("scan_rate", 0),
                "cacheHitRate": summary.get("cache_hit_rate", 0),
                "memoryUsageMB": summary.get("memory_usage_mb", 0),
                "trend": summary.get("performance_trend", "unknown"),
                "bottlenecks": summary.get("bottlenecks", []),
                "recommendations": summary.get("recommendations", []),
                "optimalWorkers": summary.get("optimal_worker_count", 4)
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"grade": "Error", "error": str(e)}
    
    @Slot(result='QVariant')
    def getOptimizationSuggestions(self):
        """Get optimization suggestions for QML"""
        try:
            suggestions = self.performance_service.get_optimization_suggestions()
            return suggestions[:5]  # Return top 5 suggestions
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {e}")
            return ["Erro ao obter sugestões de otimização"]
    
    @Slot()
    def autoOptimizePerformance(self):
        """Automatically optimize performance based on analysis"""
        try:
            analysis = self.performance_service.analyze_performance()
            
            # Auto-adjust worker count if recommended
            if analysis.optimal_worker_count != self._total_workers:
                old_workers = self._total_workers
                self._total_workers = analysis.optimal_worker_count
                self.scan_service.max_workers = analysis.optimal_worker_count
                self.updateWorkerStatus(self._active_workers, self._total_workers)
                
                logger.info(f"Auto-optimized workers: {old_workers} → {analysis.optimal_worker_count}")
            
            # Optimize cache if needed
            if "low_cache_hit_rate" in analysis.bottlenecks:
                self.optimizeCache()
            
            # Log optimization results
            logger.info(f"Auto-optimization completed: Grade {analysis.current_grade}, "
                       f"Trend: {analysis.performance_trend}")
            
        except Exception as e:
            error_msg = f"Erro na otimização automática: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(result=bool)
    def isPerformanceDegrading(self):
        """Check if performance is degrading over time"""
        try:
            return self.performance_service.is_performance_degrading()
        except Exception as e:
            logger.error(f"Error checking performance degradation: {e}")
            return False
    
    @Slot(result='QVariant')
    def getBatchQueueStatus(self):
        """Get batch queue status for QML"""
        try:
            status = self.batch_service.get_queue_status()
            jobs = self.batch_service.get_all_jobs()

            completed_jobs = sum(1 for job in jobs if job.status.value == "completed")
            failed_jobs = sum(1 for job in jobs if job.status.value == "failed")
            finished_jobs = [job for job in jobs if job.status.value in {"completed", "failed", "cancelled"}]

            avg_time_per_item = 0.0
            item_durations = [item.duration_seconds for job in finished_jobs for item in job.items if item.duration_seconds > 0]
            if item_durations:
                avg_time_per_item = sum(item_durations) / len(item_durations)

            total_processed = completed_jobs + failed_jobs
            success_rate = (completed_jobs / total_processed) if total_processed > 0 else 0.0

            return {
                "serviceRunning": status.get("service_running", False),
                "activeJobs": status.get("running_jobs", 0),
                "queueSize": status.get("queue_size", 0),
                "runningJobs": status.get("running_jobs", 0),
                "pendingJobs": status.get("pending_jobs", 0),
                "queuedJobs": status.get("queued_jobs", 0),
                "totalJobs": status.get("total_jobs", 0),
                "completedJobs": completed_jobs,
                "failedJobs": failed_jobs,
                "successRate": success_rate,
                "averageTimePerItem": avg_time_per_item,
            }
        except Exception as e:
            logger.error(f"Error getting batch queue status: {e}")
            return {"serviceRunning": False, "error": str(e)}
    
    @Slot(result='QVariant')
    def getAllBatchJobs(self):
        """Get all batch jobs for QML"""
        try:
            jobs = self.batch_service.get_all_jobs()
            return [{
                "jobId": job.job_id,
                "job_id": job.job_id,
                "title": job.title,
                "description": job.description,
                "status": job.status.value,
                "progress": job.total_progress,
                "totalProgress": job.total_progress,
                "items": [item.item_id for item in job.items],
                "itemsTotal": len(job.items),
                "itemsCompleted": job.items_completed,
                "itemsFailed": job.items_failed,
                "duration": job.duration_seconds
            } for job in jobs]
        except Exception as e:
            logger.error(f"Error getting batch jobs: {e}")
            return []
    
    @Slot(str, result=bool)
    def pauseBatchJob(self, job_id: str):
        """Pause a batch job"""
        try:
            result = self.batch_service.pause_job(job_id)
            if result:
                self._update_batch_status()
            return result
        except Exception as e:
            logger.error(f"Error pausing batch job: {e}")
            return False
    
    @Slot(str, result=bool)
    def resumeBatchJob(self, job_id: str):
        """Start pending job or resume a paused batch job."""
        try:
            if self._is_shutting_down:
                return False

            job = self.batch_service.get_job(job_id)
            if job is None:
                return False

            if job.status.value == "pending":
                task = self._schedule_task(self.batch_service.submit_job(job_id))
                if task is None:
                    return False
                self._update_batch_status()
                return True

            if job.status.value == "paused":
                resumed = self.batch_service.resume_job(job_id)
                if not resumed:
                    return False
                task = self._schedule_task(self.batch_service.submit_job(job_id))
                if task is None:
                    # Roll back optimistic resume when enqueue scheduling fails.
                    self.batch_service.pause_job(job_id)
                    return False
                self._update_batch_status()
                return True

            return False
        except Exception as e:
            logger.error(f"Error resuming batch job: {e}")
            return False
    
    @Slot(str, result=bool)
    def cancelBatchJob(self, job_id: str):
        """Cancel a batch job"""
        try:
            result = self.batch_service.cancel_job(job_id)
            if result:
                self._update_batch_status()
            return result
        except Exception as e:
            logger.error(f"Error cancelling batch job: {e}")
            return False
    
    @Slot(str, result=bool)
    def deleteBatchJob(self, job_id: str):
        """Delete a completed batch job"""
        try:
            result = self.batch_service.delete_job(job_id)
            if result:
                self._update_batch_status()
            return result
        except Exception as e:
            logger.error(f"Error deleting batch job: {e}")
            return False

    @Slot()
    def startAllBatchJobs(self):
        """Submit all pending batch jobs for processing."""
        if self._is_shutting_down:
            self.error.emit("Backend em desligamento; nao e possivel iniciar jobs em lote")
            return

        task = self._schedule_task(self._start_all_batch_jobs_async())
        if task is None:
            self.error.emit("Erro ao iniciar jobs em lote")

    async def _start_all_batch_jobs_async(self) -> None:
        submitted = 0
        try:
            if self._is_shutting_down:
                return

            for job in self.batch_service.get_all_jobs():
                if self._is_shutting_down:
                    break
                if job.status.value == "pending":
                    ok = await self.batch_service.submit_job(job.job_id)
                    if ok:
                        submitted += 1
            self._update_batch_status()
            logger.info(f"Submitted {submitted} pending batch jobs")
        except Exception as exc:
            logger.error(f"Error starting batch jobs: {exc}")
            self.error.emit(f"Erro ao iniciar jobs em lote: {exc}")

    @Slot(result=int)
    def pauseAllRunningBatchJobs(self):
        """Pause all currently running batch jobs."""
        paused = 0
        try:
            for job in self.batch_service.get_all_jobs():
                if job.status.value == "running" and self.batch_service.pause_job(job.job_id):
                    paused += 1
            self._update_batch_status()
            logger.info(f"Paused {paused} running batch jobs")
            return paused
        except Exception as exc:
            logger.error(f"Error pausing running batch jobs: {exc}")
            self.error.emit(f"Erro ao pausar jobs em lote: {exc}")
            return 0

    @Slot()
    def retryFailedBatchJobs(self):
        """Reset failed/cancelled jobs to pending and submit them again."""
        if self._is_shutting_down:
            self.error.emit("Backend em desligamento; nao e possivel reagendar jobs")
            return

        previous_states: Dict[str, Dict[str, Any]] = {}
        try:
            from core.services.batch_service import BatchJobStatus

            retry_job_ids: List[str] = []
            for job in self.batch_service.get_all_jobs():
                if job.status.value not in {"failed", "cancelled"}:
                    continue

                previous_states[job.job_id] = {
                    "job_status": job.status,
                    "job_total_progress": job.total_progress,
                    "job_start_time": job.start_time,
                    "job_completion_time": job.completion_time,
                    "item_states": [
                        {
                            "status": item.status,
                            "progress": item.progress,
                            "error_message": item.error_message,
                            "start_time": item.start_time,
                            "completion_time": item.completion_time,
                        }
                        for item in job.items
                    ],
                }

                # Apply state transition synchronously so immediate CLEAR clicks
                # cannot delete jobs that were explicitly requested for retry.
                job.status = BatchJobStatus.PENDING
                job.total_progress = 0.0
                job.start_time = None
                job.completion_time = None

                for item in job.items:
                    item.status = BatchJobStatus.PENDING
                    item.progress = 0.0
                    item.error_message = None
                    item.start_time = None
                    item.completion_time = None

                retry_job_ids.append(job.job_id)

            self._update_batch_status()

        except Exception as exc:
            logger.error(f"Error preparing retry for failed batch jobs: {exc}")
            self.error.emit(f"Erro ao preparar reagendamento de jobs falhos: {exc}")
            return

        task = self._schedule_task(self._retry_failed_batch_jobs_async(retry_job_ids))
        if task is None:
            # Roll back optimistic transition when task scheduling fails.
            for job_id in retry_job_ids:
                job = self.batch_service.get_job(job_id)
                previous = previous_states.get(job_id)
                if not job or not previous:
                    continue

                job.status = previous["job_status"]
                job.total_progress = previous["job_total_progress"]
                job.start_time = previous["job_start_time"]
                job.completion_time = previous["job_completion_time"]

                for item, item_state in zip(job.items, previous["item_states"]):
                    item.status = item_state["status"]
                    item.progress = item_state["progress"]
                    item.error_message = item_state["error_message"]
                    item.start_time = item_state["start_time"]
                    item.completion_time = item_state["completion_time"]

            self._update_batch_status()
            self.error.emit("Erro ao reagendar jobs falhos")

    async def _retry_failed_batch_jobs_async(self, retry_job_ids: List[str]) -> None:
        retried = 0
        try:
            for job_id in retry_job_ids:
                if self._is_shutting_down:
                    break
                ok = await self.batch_service.submit_job(job_id)
                if ok:
                    retried += 1

            self._update_batch_status()
            logger.info(f"Retried {retried} failed/cancelled batch jobs")
        except Exception as exc:
            logger.error(f"Error retrying failed batch jobs: {exc}")
            self.error.emit(f"Erro ao reagendar jobs falhos: {exc}")

    @Slot(result=int)
    def clearFinishedBatchJobs(self):
        """Delete completed/failed/cancelled jobs from history."""
        deleted = 0
        try:
            for job in list(self.batch_service.get_all_jobs()):
                if job.status.value in {"completed", "failed", "cancelled"}:
                    if self.batch_service.delete_job(job.job_id):
                        deleted += 1
            self._update_batch_status()
            logger.info(f"Deleted {deleted} finished batch jobs")
            return deleted
        except Exception as exc:
            logger.error(f"Error clearing finished batch jobs: {exc}")
            self.error.emit(f"Erro ao limpar jobs finalizados: {exc}")
            return 0
    
    async def _reload_hosts_async(self):
        """Async version of reload hosts"""
        try:
            # HostManager emits Qt signals; keep it on the main thread.
            self.host_manager.reload_hosts()
            self._sync_uploader_hosts_from_manager()
            await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"Error reloading hosts: {e}")
            self.error.emit(f"Erro ao recarregar hosts: {str(e)}")
    
    @Slot()
    def selectRootFolder(self):
        """Trigger QML folder selection dialog for root manga folder"""
        try:
            current_folder = self.config_manager.config.root_folder
            if current_folder and Path(current_folder).exists():
                start_dir = str(current_folder)
            else:
                start_dir = str(Path.home())
            
            # Emit signal to trigger QML FolderDialog
            self.openRootFolderDialog.emit(start_dir)
        except Exception as e:
            logger.error(f"Error opening root folder dialog: {e}")
    
    @Slot(str)
    def setRootFolder(self, folder_path: str):
        """Set root folder from QML dialog result"""
        try:
            if folder_path:
                # Clean QML file:// URLs if present
                clean_path = self._clean_file_url(folder_path)
                self.config_handler.set_root_folder(clean_path)
                logger.info(f"Root folder set to: {clean_path}")
        except Exception as e:
            logger.error(f"Error setting root folder: {e}")
    
    @Slot()
    def selectOutputFolder(self):
        """Trigger QML folder selection dialog for output metadata folder"""
        try:
            current_folder = self.config_manager.config.output_folder
            if current_folder and Path(current_folder).exists():
                start_dir = str(current_folder)
            else:
                start_dir = str(Path.home())
            
            # Emit signal to trigger QML FolderDialog
            self.openOutputFolderDialog.emit(start_dir)
        except Exception as e:
            logger.error(f"Error opening output folder dialog: {e}")
    
    @Slot(str)
    def setOutputFolder(self, folder_path: str):
        """Set output folder from QML dialog result"""
        try:
            if folder_path:
                # Clean QML file:// URLs if present
                clean_path = self._clean_file_url(folder_path)
                self.config_handler.set_output_folder(clean_path)
                logger.info(f"Output folder set to: {clean_path}")
        except Exception as e:
            logger.error(f"Error setting output folder: {e}")
    
    @Slot(str)
    def selectManga(self, manga_title: str):
        """Select manga (delegated to MangaManager)"""
        self.manga_manager.select_manga(manga_title)
        # Update manga info for QML
        self._update_manga_info_from_current()
    
    @Slot(list)
    def setSelectedChapters(self, chapter_indices: List[int]):
        """Set selected chapters (delegated to MangaManager)"""
        self.manga_manager.set_selected_chapters(chapter_indices)
    
    @Slot()
    def _toggleChapterOrder_legacy(self):
        """Toggle chapter order (delegated to MangaManager)"""
        self.manga_manager.toggle_chapter_order()
    
    @Slot(result=str)
    def getMangaInfo(self) -> str:
        """Get manga info (delegated to MangaManager)"""
        return cast(str, self.manga_manager.get_manga_info())
    
    # === LEGACY PROPERTIES AND METHODS ===
    # TODO: Migrate these to handlers
    
    @Property(float, notify=progressChanged)
    def uploadProgress(self):
        return self._upload_progress
    
    @Property(QObject, constant=True)
    def githubFolderModel(self):
        return self.github_folder_model
    
    @Property(list, notify=githubFoldersChanged)
    def githubFolders(self):
        return getattr(self, '_github_folders', ["metadata"])
    
    @Property(object, notify=mangaInfoChanged)
    def mangaInfo(self):
        return self._manga_info
    
    # Manga info properties for QML compatibility
    @Property(str, notify=mangaInfoChanged)
    def currentMangaTitle(self):
        return self._manga_info.get("title", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaDescription(self):
        return self._manga_info.get("description", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaArtist(self):
        return self._manga_info.get("artist", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaAuthor(self):
        return self._manga_info.get("author", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaGroup(self):
        return self._manga_info.get("group", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaCover(self):
        return self._manga_info.get("cover", "")
    
    @Property(str, notify=mangaInfoChanged)
    def currentMangaStatus(self):
        return cast(str, self._manga_info.get("status", ""))
    
    @Property(int, notify=mangaInfoChanged)
    def currentMangaChapterCount(self):
        return self._manga_info.get("chapterCount", 0)
    
    @Property(bool, notify=mangaInfoChanged)
    def currentMangaHasJson(self):
        # First check cached value
        cached_value = self._manga_info.get("hasJson", False)
        
        # BULLETPROOF: If cached value is False, double-check actual file system
        # This ensures we never have false negatives after save operations
        if not cached_value:
            actual_exists = self._check_json_exists_for_current_manga()
            if actual_exists:
                logger.warning("🔧 CACHE MISMATCH DETECTED: cached=False but JSON exists! Fixing cache...")
                # Update cache to reflect reality
                self._manga_info["hasJson"] = True
                cached_value = True
        
        if self._last_logged_has_json != bool(cached_value):
            logger.debug(f"🔍 QML requesting currentMangaHasJson: {cached_value}")
            self._last_logged_has_json = bool(cached_value)
        return cached_value
    
    # === MISSING CRITICAL METHODS ===
    
    @Slot()
    def initialize_async_services(self):
        """Initialize async services after event loop is ready"""
        scheduled = self._schedule_task(self.upload_queue.start())
        if scheduled is None:
            logger.debug("Async service init skipped (event loop unavailable)")
    
    @Slot()
    def loadConfig(self):
        """Load configuration on startup"""
        try:
            current_config = self.config_manager.config
            old_runtime_signature = (
                current_config.selected_host,
                current_config.github,
                {name: cfg.model_dump() for name, cfg in current_config.hosts.items()},
            )

            loaded_config = self.config_manager.load_config()
            self.config_manager.config = loaded_config

            new_runtime_signature = (
                loaded_config.selected_host,
                loaded_config.github,
                {name: cfg.model_dump() for name, cfg in loaded_config.hosts.items()},
            )

            # Keep runtime services aligned only when runtime-relevant config changed.
            if old_runtime_signature != new_runtime_signature:
                self.host_manager.reload_hosts()
                self._sync_uploader_hosts_from_manager()
                self.github_manager._init_github_service()

            self.configChanged.emit()
            self.selectedHostIndexChanged.emit()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.error.emit(f"Erro ao carregar configuração: {e}")
    
    @Slot()
    def saveConfig(self):
        """Save current configuration"""
        self.config_manager.save_config()
        self.configChanged.emit()
    
    @Slot()
    def startUpload(self):
        """Start uploading selected chapters (legacy method)"""
        default_metadata = {
            "title": self.manga_manager.current_manga.title if self.manga_manager.current_manga else "",
            "description": "",
            "artist": "",
            "author": "",
            "cover": "",
            "status": "Em Andamento"
        }
        self.startUploadWithMetadata(default_metadata)
    
    @Slot('QVariant', result=bool)
    def startUploadWithMetadata(self, metadata):
        """Start uploading selected chapters with metadata"""
        processing_started = False
        try:
            monitor_task = self._current_upload_monitor_task
            if self._current_job_id is not None or (monitor_task and not monitor_task.done()):
                self.error.emit("Upload ja esta em andamento")
                return False

            if not self.manga_manager.current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return False
            
            selected_chapters = self.manga_manager.getSelectedChapters()
            if not selected_chapters:
                self.error.emit("Nenhum capítulo selecionado")
                return False
            
            # Convert QJSValue to Python dict if needed
            if isinstance(metadata, QJSValue):
                metadata_dict = metadata.toVariant()
            elif hasattr(metadata, 'toVariant'):
                metadata_dict = metadata.toVariant()
            else:
                metadata_dict = metadata
            
            if not isinstance(metadata_dict, dict):
                error_msg = f"Dados de metadados inválidos: {type(metadata_dict)}"
                self.error.emit(error_msg)
                return False
            
            # Fix escaped newlines
            if 'description' in metadata_dict and isinstance(metadata_dict['description'], str):
                metadata_dict['description'] = metadata_dict['description'].replace('\\n', '\n')
            
            self._upload_metadata = metadata_dict
            self._emit_processing_started()
            processing_started = True
            
            # Add to queue
            task = self._schedule_task(self._queue_upload(selected_chapters))
            if task is None:
                self.error.emit("Erro ao agendar upload")
                self._emit_processing_finished()
                return False

            return True
            
        except Exception as e:
            logger.error(f"Error in startUploadWithMetadata: {e}")
            self.error.emit(f"Erro ao iniciar upload: {str(e)}")
            if processing_started:
                self._emit_processing_finished()
            return False
    
    async def _queue_upload(self, selected_chapters: List[str]):
        """Queue upload job"""
        try:
            job_id = await self.upload_queue.add_job(
                self._upload_async,
                selected_chapters
            )
            self._current_job_id = job_id
            monitor_task = self._schedule_task(self._monitor_job(job_id))
            if monitor_task is None:
                # Fallback: monitor in this task so UI state can still be finalized.
                await self._monitor_job(job_id)
            else:
                self._current_upload_monitor_task = monitor_task
        except Exception as e:
            self.error.emit(f"Erro ao enfileirar upload: {str(e)}")
            self._emit_processing_finished()
    
    async def _monitor_job(self, job_id: str):
        """Monitor upload job progress"""
        try:
            while True:
                try:
                    job = await self.upload_queue.wait_for_job(job_id, timeout=1.0)
                    if job:
                        if job.status.value == "completed":
                            self._upload_progress = 1.0
                            self.progressChanged.emit(1.0)
                            self._emit_processing_finished()
                            break
                        elif job.status.value == "failed":
                            self.error.emit(f"Upload failed: {job.error}")
                            self._emit_processing_finished()
                            break
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.5)
        finally:
            if self._current_job_id == job_id:
                self._current_job_id = None
            current_task = asyncio.current_task()
            if self._current_upload_monitor_task is current_task:
                self._current_upload_monitor_task = None
    
    async def _upload_async(self, selected_chapters: List[str]):
        """Async upload handler"""
        from core.models import Chapter

        current_manga = self.manga_manager.current_manga
        if current_manga is None:
            raise ValueError("Nenhum mangá selecionado")

        chapters_to_upload = []
        for chapter_name in selected_chapters:
            chapter_path = current_manga.path / chapter_name
            if chapter_path.exists():
                chapter = Chapter(name=chapter_name, path=chapter_path, images=[])
                chapters_to_upload.append(chapter)

        if not chapters_to_upload:
            raise ValueError("Nenhum capítulo válido selecionado")

        # Set host in uploader service
        current_host = self.host_manager.get_current_host()
        if not current_host:
            raise ValueError("Nenhum host configurado")

        self.uploader_service.register_host(self.host_manager.selectedHost, current_host)
        self.uploader_service.set_host(self.host_manager.selectedHost)

        # Upload
        results = await self.uploader_service.upload_manga(
            current_manga,
            chapters_to_upload
        )

        # Generate metadata
        output_path = self.config_manager.config.output_folder / current_manga.title / f"{current_manga.title}.json"
        update_mode = self.config_manager.config.json_update_mode
        saved_json_path = await self.uploader_service.generate_metadata(
            current_manga,
            results,
            output_path,
            update_mode,
            self._upload_metadata
        )

        self._last_json_path = saved_json_path

        # Auto-upload to GitHub if configured
        if self.github_manager.is_github_configured():
            # Keep the queued upload lifecycle consistent: only mark upload as finished
            # after the optional automatic GitHub publish step completes.
            await self._upload_to_github(saved_json_path)
    
    async def _upload_to_github(self, json_file: Path):
        """Upload metadata file to GitHub - ENHANCED WITH BETTER FEEDBACK"""
        github_service = None
        try:
            github_config = self.config_manager.config.github
            
            # Clean configuration values (remove problematic characters)
            def clean_string(s):
                return str(s).strip().replace('\n', '').replace('\r', '').replace('\t', '')
            
            token = clean_string(github_config.get("token", ""))
            repo = clean_string(github_config.get("repo", ""))
            branch = clean_string(github_config.get("branch", "main"))
            
            if not token or not repo:
                error_msg = "Configuração do GitHub incompleta (token ou repositório em branco)"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            if not json_file.exists():
                error_msg = f"Arquivo não encontrado: {json_file}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            from core.services.github import GitHubService
            
            github_service = GitHubService(
                token=token,
                repo=repo,
                branch=branch
            )
            
            # Verify service is configured
            if not github_service.configured:
                error_msg = "Serviço do GitHub não foi configurado corretamente"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            # Create remote path using configured folder
            github_folder = clean_string(github_config.get("folder", "metadata"))
            remote_path = f"{github_folder}/{json_file.name}" if github_folder else json_file.name
            commit_message = clean_string(github_config.get("commit_message", f"Update manga metadata: {json_file.stem}"))
            
            logger.info(f"Iniciando upload GitHub: {json_file.name} → {repo}/{remote_path}")
            
            # Attempt the upload
            success = await github_service.upload_file(
                json_file, remote_path, commit_message
            )
            
            if success:
                success_msg = f"✅ Arquivo {json_file.name} enviado com sucesso para {repo}"
                logger.success(success_msg)
            else:
                error_msg = f"❌ Falha no upload para GitHub: {repo}/{remote_path}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Erro no upload GitHub: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
        finally:
            # Always cleanup GitHub service
            if github_service:
                try:
                    await github_service.close()
                    logger.debug("GitHub service connection closed")
                except Exception as cleanup_error:
                    logger.debug(f"Error during GitHub service cleanup: {cleanup_error}")
    
    
    @Slot(str, result=str)
    def makeJsonSafe(self, text: str) -> str:
        """Convert text to JSON-safe format"""
        if not text:
            return ""
        
        safe_text = text.replace('\\', '\\\\')
        safe_text = safe_text.replace('"', '\\"')
        safe_text = safe_text.replace('\n', '\\n')
        safe_text = safe_text.replace('\r', '\\r')
        safe_text = safe_text.replace('\t', '\\t')
        
        return safe_text
    
    
    @Slot('QVariant', result=bool)
    def updateExistingMetadata(self, metadata):
        """Update existing metadata file"""
        try:
            if not self.manga_manager.current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return False
            
            # Convert QJSValue to dict
            if isinstance(metadata, QJSValue):
                metadata_dict = metadata.toVariant()
            else:
                metadata_dict = metadata
            
            if not isinstance(metadata_dict, dict):
                self.error.emit("Dados de metadados inválidos")
                return False
            
            # Fix escaped newlines
            if 'description' in metadata_dict:
                metadata_dict['description'] = metadata_dict['description'].replace('\\n', '\n')
            
            # Update metadata via manga manager
            self.manga_manager.update_metadata(metadata_dict)
            
            # Update local manga info
            self._update_manga_info_from_current()
            
            # BULLETPROOF: Emit signal to force GitHub button refresh
            self.metadataUpdateCompleted.emit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            self.error.emit(f"Erro ao atualizar metadados: {str(e)}")
            return False
    
    def _init_hosts(self):
        """Initialize hosts"""
        if not self.host_manager.hosts:
            self.host_manager.reload_hosts()
        else:
            logger.debug("Reusing already initialized hosts from HostManager")

        self._sync_uploader_hosts_from_manager()

    def _sync_uploader_hosts_from_manager(self) -> None:
        """Sync uploader host registry with HostManager instances."""
        for host_name in self.host_manager.host_list:
            host_instance = self.host_manager.get_host(host_name)
            if host_instance:
                self.uploader_service.register_host(host_name, host_instance)

        self.uploader_service.set_host(self.config_manager.config.selected_host)
    
    def _init_github_folders(self):
        """Initialize GitHub folders on startup if configured - CRITICAL"""
        try:
            if self.github_manager.is_github_configured():
                # Auto-refresh folders on startup
                self.github_manager.refreshGitHubFolders()
                logger.debug("Initiated GitHub folders refresh on startup")
            else:
                # Set fallback folders for non-configured GitHub
                self._github_folders = ["", "metadata"]
                logger.debug("GitHub not configured, using fallback folder options")
        except Exception as e:
            logger.error(f"Error initializing GitHub folders: {e}")
            # Ensure fallback folders are available
            self._github_folders = ["", "metadata"]
    
    def _init_performance_monitoring(self):
        """Initialize performance monitoring with realistic defaults"""
        try:
            from PySide6.QtCore import QTimer
            
            # Set initial values based on current configuration
            current_host = self.config_manager.config.selected_host
            host_config = self.config_manager.config.hosts.get(current_host)
            if host_config:
                self._total_workers = getattr(host_config, 'max_workers', 5)
            else:
                self._total_workers = 5
            
            self._active_workers = 0
            self._last_scan_time = "0.0s"
            self._cache_utilization = 0
            self._processing_queue = 0
            self._scan_progress = 0
            
            # Update initial memory usage
            self._update_memory_usage()
            
            # Start periodic memory monitoring (every 5 seconds)
            self._memory_timer = QTimer()
            self._memory_timer.timeout.connect(self._periodic_memory_update)
            self._memory_timer.start(5000)  # 5 seconds
            
            logger.debug(f"Performance monitoring initialized: {self._total_workers} workers, {self._memory_usage} memory")
            
        except Exception as e:
            logger.error(f"Error initializing performance monitoring: {e}")
    
    def _periodic_memory_update(self):
        """Periodically update memory usage for footer display"""
        try:
            old_usage = self._memory_usage
            self._update_memory_usage()
            if old_usage != self._memory_usage:
                self.performanceChanged.emit()
        except Exception as e:
            logger.debug(f"Error in periodic memory update: {e}")
    
    def _init_batch_service(self):
        """Initialize batch processing service"""
        try:
            # Set up batch service callbacks
            self.batch_service.set_callbacks(
                job_progress_callback=self._on_batch_job_progress,
                job_completed_callback=self._on_batch_job_completed,
                item_completed_callback=self._on_batch_item_completed
            )
            
            # Start batch service
            task = self._schedule_task(self.batch_service.start_service())
            if task is None:
                logger.warning("Could not schedule batch service startup")
            
            # Update initial batch status
            self._update_batch_status()
            
            logger.debug("Batch service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing batch service: {e}")
    
    def _on_batch_job_progress(self, job_id: str, progress: float):
        """Callback for batch job progress updates"""
        try:
            self._update_batch_status()
            logger.debug(f"Batch job {job_id}: {progress:.1f}% complete")
        except Exception as e:
            logger.error(f"Error in batch job progress callback: {e}")
    
    def _on_batch_job_completed(self, job_id: str, job):
        """Callback for batch job completion"""
        try:
            self._update_batch_status()
            logger.info(f"Batch job completed: {job.title} ({job.success_rate:.1f}% success)")
        except Exception as e:
            logger.error(f"Error in batch job completion callback: {e}")
    
    def _on_batch_item_completed(self, job_id: str, item_id: str, item):
        """Callback for batch item completion"""
        try:
            logger.debug(f"Batch item completed: {item.manga_title}")
        except Exception as e:
            logger.error(f"Error in batch item completion callback: {e}")
    
    def _update_batch_status(self):
        """Update batch status properties"""
        try:
            status = self.batch_service.get_queue_status()
            
            old_queue_size = self._batch_queue_size
            old_active_jobs = self._batch_active_jobs
            
            self._batch_queue_size = status.get("queue_size", 0)
            self._batch_active_jobs = status.get("running_jobs", 0)
            
            # Emit signals if values changed
            if old_queue_size != self._batch_queue_size or old_active_jobs != self._batch_active_jobs:
                self.performanceChanged.emit()
            
        except Exception as e:
            logger.error(f"Error updating batch status: {e}")

    async def shutdown(self) -> None:
        """Gracefully stop background activity and close async services."""
        if self._is_shutting_down:
            logger.debug("Backend shutdown already in progress; skipping duplicate request")
            return

        logger.info("Backend shutdown started")
        self._is_shutting_down = True
        try:
            if self._memory_timer is not None:
                self._memory_timer.stop()
                self._memory_timer.deleteLater()
                self._memory_timer = None

            if self.scan_service.is_scanning:
                try:
                    await self.scan_service.cancel_scan()
                except Exception as exc:
                    logger.warning(f"Error cancelling active scan during shutdown: {exc}")

            if self._current_scan_task and not self._current_scan_task.done():
                self._current_scan_task.cancel()
                await asyncio.gather(self._current_scan_task, return_exceptions=True)
            self._current_scan_task = None

            try:
                await self.batch_service.stop_service()
            except Exception as exc:
                logger.warning(f"Error stopping batch service during shutdown: {exc}")

            try:
                monitor_task = self._current_upload_monitor_task
                if monitor_task and not monitor_task.done():
                    monitor_task.cancel()
                    await asyncio.gather(monitor_task, return_exceptions=True)
                self._current_upload_monitor_task = None
                self._current_job_id = None

                await self.upload_queue.stop()
            except Exception as exc:
                logger.warning(f"Error stopping upload queue during shutdown: {exc}")

            background_tasks = [task for task in self._background_tasks if not task.done()]
            for task in background_tasks:
                task.cancel()
            if background_tasks:
                await asyncio.gather(*background_tasks, return_exceptions=True)
            self._background_tasks.clear()

            github_service = self.github_manager.github_service
            if github_service is not None:
                try:
                    await github_service.close()
                except Exception as exc:
                    logger.warning(f"Error closing GitHub service during shutdown: {exc}")
        finally:
            self._is_shutting_down = False
            logger.info("Backend shutdown finished")
    
    # Legacy methods for compatibility
    @Slot(list)
    def uploadSelectedChapters(self, chapter_indices: List[int]):
        """Legacy method - use startUpload instead"""
        logger.info(f"Legacy upload requested for {len(chapter_indices)} chapters")
        self.manga_manager.set_selected_chapters(chapter_indices)
        self.startUpload()
    
    @Slot()
    def stopUpload(self):
        """Stop current upload"""
        logger.info("Upload stop requested")
        task = self._schedule_task(self._stop_upload_async())
        if task is None:
            self.error.emit("Erro ao interromper upload")

    async def _stop_upload_async(self) -> None:
        """Stop current upload queue processing and reset upload state."""
        try:
            monitor_task = self._current_upload_monitor_task
            if monitor_task and not monitor_task.done():
                monitor_task.cancel()
                await asyncio.gather(monitor_task, return_exceptions=True)
            self._current_upload_monitor_task = None

            await self.upload_queue.stop()
            await self.upload_queue.start()

            self._current_job_id = None
            self._upload_progress = 0.0
            self.progressChanged.emit(0.0)
            logger.info("Upload queue restarted after stop request")
        except Exception as exc:
            logger.error(f"Error stopping upload: {exc}")
            self.error.emit(f"Erro ao interromper upload: {exc}")
        finally:
            self._emit_processing_finished()
    
    @Slot(str)
    def filterMangaList(self, search_text: str):
        """Filter manga list (delegated to MangaManager)"""
        self.manga_manager.filterMangaList(search_text)
    
    @Slot(str)
    def loadMangaDetails(self, manga_path: str):
        """Load manga details (delegated to MangaManager)"""
        self.manga_manager.loadMangaDetails(manga_path)
    
    @Slot()
    def selectAllChapters(self):
        """Select all chapters (delegated to MangaManager) - CRITICAL"""
        try:
            self.manga_manager.selectAllChapters()
            logger.debug("Selected all chapters")
        except Exception as e:
            logger.error(f"Error selecting all chapters: {e}")
    
    @Slot()
    def unselectAllChapters(self):
        """Unselect all chapters (delegated to MangaManager) - CRITICAL"""
        try:
            self.manga_manager.unselectAllChapters()
            logger.debug("Unselected all chapters")
        except Exception as e:
            logger.error(f"Error unselecting all chapters: {e}")
    
    @Slot()
    def toggleChapterOrder(self):
        """Toggle chapter order (delegated to MangaManager) - CRITICAL"""
        try:
            self.manga_manager.toggle_chapter_order()
            logger.debug("Toggled chapter order")
        except Exception as e:
            logger.error(f"Error toggling chapter order: {e}")
    
    
    # Cookie test functionality
    cookieTestResult = Signal(str, str)  # (result_type, message)
    
    @Slot(str)
    def testImgboxCookie(self, cookie):
        """Test Imgbox cookie by attempting a small upload"""
        cookie_value = str(cookie or "").strip()

        def run_test():
            try:
                import tempfile
                from pathlib import Path

                if not cookie_value:
                    self.cookieTestResult.emit("error", "❌ Cookie vazio")
                    return

                # Basic sanity check to avoid obvious false positives.
                if "=" not in cookie_value or len(cookie_value) < 10:
                    self.cookieTestResult.emit("error", "❌ Cookie inválido (formato inesperado)")
                    return
                
                # Create a minimal test file
                with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(b'test')
                
                # Test basic functionality
                try:
                    import importlib.util
                    if importlib.util.find_spec("pyimgbox") is None:
                        raise ImportError("pyimgbox not installed")
                    self.cookieTestResult.emit("success", "✅ Cookie aceito! pyimgbox funcionando corretamente")
                except ImportError:
                    self.cookieTestResult.emit("error", "❌ pyimgbox não está instalado")
                except Exception as e:
                    self.cookieTestResult.emit("error", f"❌ Erro: {str(e)}")
                
                # Clean up
                try:
                    temp_path.unlink()
                except OSError:
                    pass
                    
            except Exception as e:
                self.cookieTestResult.emit("error", f"❌ Erro no teste: {str(e)}")
        
        # Use QTimer to run test without blocking
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, run_test)
    
    def _check_json_exists_for_current_manga(self) -> bool:
        """Check if JSON file exists for the current manga - BULLETPROOF METHOD"""
        if not self.manga_manager.current_manga:
            return False
            
        try:
            from pathlib import Path
            from utils.sanitizer import sanitize_filename
            
            manga_title = self.manga_manager.current_manga.title
            output_folder = Path(self.config_manager.config.output_folder)
            manga_folder = output_folder / manga_title
            
            # Use same logic as manga_manager._load_manga_info for consistency
            
            # 0. First try in root folder (same directory as manga folder)
            root_folder = Path(self.config_manager.config.root_folder)
            sanitized_title = sanitize_filename(manga_title)
            root_json = root_folder / f"{sanitized_title}.json"
            if root_json.exists():
                logger.debug(f"✅ JSON exists in root: {root_json}")
                return True
            
            # 0.1. Also try glob search in root folder
            for file in root_folder.glob("*.json"):
                if sanitize_filename(manga_title) == sanitize_filename(file.stem):
                    logger.debug(f"✅ JSON exists in root (glob): {file}")
                    return True
            
            # 1. Try with sanitized filename in output folder
            potential_json = manga_folder / f"{sanitized_title}.json"
            if potential_json.exists():
                logger.debug(f"✅ JSON exists in manga folder: {potential_json}")
                return True
            
            # 2. If not found, try looking for any .json file in the folder
            if manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    logger.debug(f"✅ JSON exists (any): {file}")
                    return True
            
            logger.debug(f"❌ No JSON found for manga: {manga_title}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking JSON existence: {e}")
            return False

    def _update_manga_info_from_current(self):
        """Update manga info from current selected manga"""
        if self.manga_manager.current_manga:
            manga = self.manga_manager.current_manga
            chapter_count = len(getattr(manga, 'chapters', [])) or self.chapter_model.rowCount()
            
            # CRITICAL FIX: Properly determine if JSON exists instead of hardcoding False
            has_json = self._check_json_exists_for_current_manga()
            
            self._manga_info = {
                "title": manga.title,
                "description": getattr(manga, 'description', ''),
                "artist": "",
                "author": "",
                "cover": getattr(manga, 'cover_url', ''),
                "status": "",
                "group": "",
                "chapterCount": chapter_count,
                "hasJson": has_json  # Use actual JSON existence check
            }
            logger.debug(f"🔄 _update_manga_info_from_current: {manga.title} - hasJson={has_json}")
            self.mangaInfoChanged.emit()
    
    @Slot(str)
    def setFolderStructure(self, structure: str):
        """Set folder structure and rescan current manga - CRITICAL"""
        try:
            if structure in ["standard", "flat", "volume_based", "scan_manga_chapter", "scan_manga_volume_chapter"]:
                self.config_manager.config.folder_structure = structure
                self.config_manager.save_config()
                
                # Rescan current manga with new structure
                if self.manga_manager.current_manga:
                    # Reload chapters with new structure
                    self.manga_manager._load_chapters()
                    self.chapterListChanged.emit()
                
                self.configChanged.emit()
                self.manga_manager.refresh_manga_list()  # Use manga_manager method
                
                logger.info(f"Updated folder structure to: {structure}")
            else:
                logger.warning(f"Invalid folder structure: {structure}")
                
        except Exception as e:
            error_msg = f"Erro ao definir estrutura de pastas: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(str)
    def selectGitHubFolder(self, folder_path: str):
        """Select a GitHub folder and update configuration"""
        github_config = self.config_manager.config.github
        github_config["folder"] = folder_path
        self.config_manager.save_config()
        self.configChanged.emit()
        logger.info(f"GitHub folder selected: {folder_path}")
    
    @Slot()
    def debugGitHubButtonState(self):
        """Debug method to check GitHub button state - FOR TESTING"""
        try:
            has_json = self._manga_info.get('hasJson', False)
            title = self._manga_info.get('title', 'None')
            github_configured = self.github_manager.is_github_configured()
            github_repo = self.github_manager.githubRepo
            
            logger.info("=== GITHUB BUTTON STATE DEBUG ===")
            logger.info(f"Current manga: {title}")
            logger.info(f"HasJson: {has_json}")
            logger.info(f"GitHub configured: {github_configured}")
            logger.info(f"GitHub repo: {github_repo}")
            logger.info(f"Button should be: {'ENABLED' if (has_json and github_configured) else 'DISABLED'}")
            logger.info("=====================================")
            
            return f"Manga: {title} | hasJson: {has_json} | GitHub: {github_configured}"
            
        except Exception as e:
            logger.error(f"Error in debug GitHub button state: {e}")
            return f"Error: {e}"
