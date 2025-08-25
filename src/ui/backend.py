"""Refactored UI Backend - Orchestrates specialized handlers"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement, QJSValue
from pathlib import Path
import asyncio
import json
from typing import List, Dict, Optional

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
    metadataLoaded = Signal('QVariant')
    metadataUpdateCompleted = Signal()  # BULLETPROOF: Signal for GitHub button fix
    mangaInfoChanged = Signal()
    configChanged = Signal()
    mangaListChanged = Signal()
    chapterListChanged = Signal()
    selectedHostIndexChanged = Signal()
    githubFoldersChanged = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Core services
        self.config_manager = ConfigManager()
        self.uploader_service = MangaUploaderService()
        self.upload_queue = UploadQueue(max_concurrent=3)
        
        # Specialized handlers
        self.config_handler = ConfigHandler(self.config_manager)
        self.host_manager = HostManager(self.config_manager)
        self.manga_manager = MangaManager(self.config_manager, self.uploader_service)
        self.github_manager = GitHubManager(self.config_manager)
        
        # Legacy models (TODO: migrate to handlers)
        self.github_folder_model = GitHubFolderListModel(self)
        
        # Internal state
        self._upload_progress = 0.0
        self._github_folders = ["metadata"]
        self._current_job_id = None
        self._last_json_path = None
        self._upload_metadata = None
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
        
        # Connect handler signals to main signals
        self._connect_handler_signals()
        
        # Initialize services
        self._init_hosts()
        
        # CRITICAL: Initialize GitHub folders on startup if configured
        self._init_github_folders()
        
        logger.info("Backend initialized with specialized handlers")
    
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
        self._upload_progress = float(progress)
        self.progressChanged.emit(self._upload_progress)
        logger.debug(f"Upload progress for {manga_title}: {progress}%")
    
    def _on_upload_completed(self, manga_title: str):
        """Handle upload completion"""
        self.processingFinished.emit()
        logger.info(f"Upload completed for: {manga_title}")
    
    def _on_upload_failed(self, manga_title: str, error_msg: str):
        """Handle upload failure"""
        self.error.emit(error_msg)
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
    
    # === CRITICAL MISSING METHODS FROM ORIGINAL ===
    
    @Slot()
    def initialize_async_services(self):
        """Initialize async services after event loop is ready"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.upload_queue.start())
            else:
                loop.run_until_complete(self.upload_queue.start())
        except RuntimeError:
            pass
    
    @Slot()
    def loadConfig(self):
        """Load configuration on startup"""
        self.config_manager.load_config()
        self.configChanged.emit()
    
    @Slot()
    def saveConfig(self):
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
                self.host_manager.reload_hosts()
                logger.debug("Reloaded hosts after configuration change")
            
            # Refresh manga list if folder paths changed
            if "rootFolder" in config_dict or "outputFolder" in config_dict:
                self.manga_manager.refresh_manga_list()
                logger.debug("Refreshed manga list after folder path change")
            
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
    def filterMangaList(self, search_text: str):
        """Filter manga list based on search text - CRITICAL"""
        self.manga_manager.filter_manga_list(search_text)
    
    @Slot(str)
    def loadMangaDetails(self, manga_path: str):
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
    def startUpload(self):
        """Start upload process - CRITICAL"""
        try:
            if not self.manga_manager.get_selected_chapters():
                self.error.emit("Nenhum capítulo selecionado")
                return
            
            if not self.manga_manager.get_current_manga():
                self.error.emit("Nenhum mangá selecionado")
                return
            
            # Start upload through manga manager
            self.manga_manager.start_upload()
            self.processingStarted.emit()
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot('QVariant')
    def startUploadWithMetadata(self, metadata):
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
            
            # Start GitHub upload with better error handling
            asyncio.ensure_future(self._upload_to_github_safe(json_file))
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload do GitHub: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
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
                        return json_file_path
                    
                    # Try any JSON in manga folder
                    for file in manga_folder.glob("*.json"):
                        logger.debug(f"Found JSON file: {file}")
                        return file
                
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
    
    @Slot()
    def refreshGitHubFolders(self):
        """Refresh GitHub folders - CRITICAL - Delegate to GitHubManager"""
        try:
            if not self.github_manager.is_github_configured():
                logger.warning("GitHub not configured for folder refresh")
                self.error.emit("GitHub não configurado para carregar pastas")
                return
            
            # CRITICAL: Use GitHubManager's method which now properly emits signals
            self.github_manager.refreshGitHubFolders()
            logger.debug("Delegated GitHub folders refresh to GitHubManager")
            
        except Exception as e:
            logger.error(f"Error refreshing GitHub folders: {e}")
            self.error.emit(f"Erro ao carregar pastas do GitHub: {str(e)}")
    
    @Slot(str)
    def selectGitHubFolder(self, folder_path: str):
        """Select GitHub folder - CRITICAL"""
        self.github_manager.select_folder(folder_path)
    
    @Slot(str, result=str)
    def makeJsonSafe(self, text: str) -> str:
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
                    "status": metadata.get("status", "Em Andamento")
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
                    "status": "Em Andamento"
                }
                self.metadataLoaded.emit(default_metadata)
                logger.debug(f"No metadata found for {manga_title}, using defaults")
            
        except Exception as e:
            error_msg = f"Erro ao carregar metadata: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot('QVariant')
    def updateExistingMetadata(self, metadata):
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
            
            # Signal success to close the dialog
            self.processingFinished.emit()
            
            logger.info(f"✅ Metadata update completed for: {metadata_dict.get('title', 'Unknown')}")
            
        except Exception as e:
            error_msg = f"Erro ao atualizar metadata: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    @Slot(str)
    def testImgboxCookie(self, cookie):
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
        """Refresh manga list (delegated to MangaManager)"""
        self.manga_manager.refresh_manga_list()
    
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
    def toggleChapterOrder(self):
        """Toggle chapter order (delegated to MangaManager)"""
        self.manga_manager.toggle_chapter_order()
    
    @Slot(result=str)
    def getMangaInfo(self) -> str:
        """Get manga info (delegated to MangaManager)"""
        return self.manga_manager.get_manga_info()
    
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
    
    @Property('QVariant', notify=mangaInfoChanged)
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
        return self._manga_info.get("status", "")
    
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
                logger.warning(f"🔧 CACHE MISMATCH DETECTED: cached=False but JSON exists! Fixing cache...")
                # Update cache to reflect reality
                self._manga_info["hasJson"] = True
                cached_value = True
        
        logger.debug(f"🔍 QML requesting currentMangaHasJson: {cached_value}")
        return cached_value
    
    # === MISSING CRITICAL METHODS ===
    
    @Slot()
    def initialize_async_services(self):
        """Initialize async services after event loop is ready"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.upload_queue.start())
            else:
                loop.run_until_complete(self.upload_queue.start())
        except RuntimeError:
            pass
    
    @Slot()
    def loadConfig(self):
        """Load configuration on startup"""
        self.config_manager.load_config()
    
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
    
    @Slot('QVariant')
    def startUploadWithMetadata(self, metadata):
        """Start uploading selected chapters with metadata"""
        try:
            if not self.manga_manager.current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return
            
            selected_chapters = self.manga_manager.getSelectedChapters()
            if not selected_chapters:
                self.error.emit("Nenhum capítulo selecionado")
                return
            
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
                return
            
            # Fix escaped newlines
            if 'description' in metadata_dict and isinstance(metadata_dict['description'], str):
                metadata_dict['description'] = metadata_dict['description'].replace('\\n', '\n')
            
            self._upload_metadata = metadata_dict
            self.processingStarted.emit()
            
            # Add to queue
            asyncio.ensure_future(self._queue_upload(selected_chapters))
            
        except Exception as e:
            logger.error(f"Error in startUploadWithMetadata: {e}")
            self.error.emit(f"Erro ao iniciar upload: {str(e)}")
    
    async def _queue_upload(self, selected_chapters: List[str]):
        """Queue upload job"""
        try:
            job_id = await self.upload_queue.add_job(
                self._upload_async,
                selected_chapters
            )
            asyncio.ensure_future(self._monitor_job(job_id))
        except Exception as e:
            self.error.emit(f"Erro ao enfileirar upload: {str(e)}")
    
    async def _monitor_job(self, job_id: str):
        """Monitor upload job progress"""
        while True:
            try:
                job = await self.upload_queue.wait_for_job(job_id, timeout=1.0)
                if job:
                    if job.status.value == "completed":
                        self._upload_progress = 1.0
                        self.progressChanged.emit(1.0)
                        self.processingFinished.emit()
                        break
                    elif job.status.value == "failed":
                        self.error.emit(f"Upload failed: {job.error}")
                        self.processingFinished.emit()
                        break
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.5)
    
    async def _upload_async(self, selected_chapters: List[str]):
        """Async upload handler"""
        try:
            from core.models import Chapter
            
            chapters_to_upload = []
            current_manga = self.manga_manager.current_manga
            
            for chapter_name in selected_chapters:
                chapter_path = current_manga.path / chapter_name
                if chapter_path.exists():
                    chapter = Chapter(name=chapter_name, path=chapter_path, images=[])
                    chapters_to_upload.append(chapter)
            
            if not chapters_to_upload:
                self.error.emit("Nenhum capítulo válido selecionado")
                return
            
            # Set host in uploader service
            current_host = self.host_manager.get_current_host()
            if not current_host:
                self.error.emit("Nenhum host configurado")
                return
            
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
                asyncio.ensure_future(self._upload_to_github(saved_json_path))
            
            self.processingFinished.emit()
            
        except Exception as e:
            self.error.emit(f"Erro no upload: {str(e)}")
            self.processingFinished.emit()
    
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
                # Use processingFinished to indicate success to QML
                self.processingFinished.emit()
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
    
    
    @Slot('QVariant')
    def updateExistingMetadata(self, metadata):
        """Update existing metadata file"""
        try:
            if not self.manga_manager.current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return
            
            # Convert QJSValue to dict
            if isinstance(metadata, QJSValue):
                metadata_dict = metadata.toVariant()
            else:
                metadata_dict = metadata
            
            if not isinstance(metadata_dict, dict):
                self.error.emit("Dados de metadados inválidos")
                return
            
            # Fix escaped newlines
            if 'description' in metadata_dict:
                metadata_dict['description'] = metadata_dict['description'].replace('\\n', '\n')
            
            # Update metadata via manga manager
            self.manga_manager.update_metadata(metadata_dict)
            
            # Update local manga info
            self._update_manga_info_from_current()
            
            # BULLETPROOF: Emit signal to force GitHub button refresh
            self.metadataUpdateCompleted.emit()
            
            self.processingFinished.emit()
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            self.error.emit(f"Erro ao atualizar metadados: {str(e)}")
    
    def _init_hosts(self):
        """Initialize hosts"""
        self.host_manager.reload_hosts()
        
        # Register hosts with uploader service
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
    
    # Legacy methods for compatibility
    @Slot(list)
    def uploadSelectedChapters(self, chapter_indices: List[int]):
        """Legacy method - use startUpload instead"""
        logger.info(f"Upload requested for {len(chapter_indices)} chapters")
        self.processingStarted.emit()
    
    @Slot()
    def stopUpload(self):
        """Stop current upload"""
        logger.info("Upload stop requested")
    
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
        def run_test():
            try:
                import tempfile
                from pathlib import Path
                
                # Create a minimal test file
                with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(b'test')
                
                # Test basic functionality
                try:
                    import pyimgbox
                    self.cookieTestResult.emit("success", "✅ Cookie aceito! pyimgbox funcionando corretamente")
                except ImportError:
                    self.cookieTestResult.emit("error", "❌ pyimgbox não está instalado")
                except Exception as e:
                    self.cookieTestResult.emit("error", f"❌ Erro: {str(e)}")
                
                # Clean up
                try:
                    temp_path.unlink()
                except:
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
            from src.utils.sanitizer import sanitize_filename
            
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
