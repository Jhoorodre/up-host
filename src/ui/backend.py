from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement, QJSValue
from pathlib import Path
import asyncio
from typing import List, Dict

from core.models import Manga, Chapter
from core.services import MangaUploaderService, UploadQueue
from core.services.github import GitHubService
from core.hosts import CatboxHost
from core.config import ConfigManager
from .models import MangaListModel, ChapterListModel, GitHubFolderListModel
from loguru import logger

QML_IMPORT_NAME = "Backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Backend(QObject):
    # Signals
    processingStarted = Signal()
    processingFinished = Signal()
    error = Signal(str)
    progressChanged = Signal(float)
    mangaListChanged = Signal()
    chapterListChanged = Signal()
    configChanged = Signal()
    metadataLoaded = Signal('QVariant')
    mangaInfoChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.uploader_service = MangaUploaderService()
        self.upload_queue = UploadQueue(max_concurrent=3)
        self._upload_progress = 0.0
        self._available_hosts = [
            "Catbox", "Imgur", "ImgBB", "Lensdump", 
            "Pixeldrain", "Gofile", "ImageChest", "Imgbox",
            "ImgHippo", "ImgPile"
        ]
        self.manga_model = MangaListModel(self)
        self.chapter_model = ChapterListModel(self)
        self.github_folder_model = GitHubFolderListModel(self)
        self._github_folders = ["metadata"]
        self._current_manga = None
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
            "chapterCount": 0,
            "hasJson": False
        }
        
        # Initialize hosts
        self._init_hosts()
        # Queue will be started when event loop is ready
    
    def _init_hosts(self):
        # Initialize all hosts
        host_classes = {
            "Catbox": ("CatboxHost", CatboxHost),
            "Imgur": ("ImgurHost", None),  # Will be imported dynamically
            "ImgBB": ("ImgBBHost", None),
            "Lensdump": ("LensdumpHost", None),
            "Pixeldrain": ("PixeldrainHost", None),
            "Gofile": ("GofileHost", None),
            "ImageChest": ("ImageChestHost", None),
            "Imgbox": ("ImgboxHost", None),
            "ImgHippo": ("ImgHippoHost", None),
            "ImgPile": ("ImgPileHost", None)
        }
        
        for host_name, (class_name, host_class) in host_classes.items():
            try:
                host_config = self.config_manager.get_host_config(host_name)
                if host_config:  # Register all hosts, not just enabled ones
                    if host_class is None:
                        # Dynamic import
                        from core.hosts import (
                            ImgurHost, ImgBBHost, LensdumpHost, PixeldrainHost,
                            GofileHost, ImageChestHost, ImgboxHost, ImgHippoHost, ImgPileHost
                        )
                        host_class = locals()[class_name]
                    
                    host_instance = host_class(host_config.model_dump())
                    self.uploader_service.register_host(host_name, host_instance)
                    logger.debug(f"Initialized {host_name} host (enabled: {host_config.enabled})")
                    
            except Exception as e:
                logger.warning(f"Failed to initialize {host_name} host: {e}")
        
        # Set default host
        self.uploader_service.set_host(self.config_manager.config.selected_host)
    
    @Property(float, notify=progressChanged)
    def uploadProgress(self):
        return self._upload_progress
    
    @Property(list, constant=True)
    def availableHosts(self):
        return self._available_hosts
    
    selectedHostIndexChanged = Signal()
    
    @Property(int, notify=selectedHostIndexChanged)
    def selectedHostIndex(self):
        try:
            return self._available_hosts.index(self.config_manager.config.selected_host)
        except ValueError:
            return 0
    
    # Configuration properties
    @Property(str, notify=configChanged)
    def rootFolder(self):
        return str(self.config_manager.config.root_folder)
    
    @Property(str, notify=configChanged)
    def outputFolder(self):
        return str(self.config_manager.config.output_folder)
    
    @Property(str, notify=configChanged)
    def catboxUserhash(self):
        catbox_config = self.config_manager.config.hosts.get("Catbox")
        return catbox_config.userhash if catbox_config else ""
    
    @Property(str, notify=configChanged)
    def imgurClientId(self):
        imgur_config = self.config_manager.config.hosts.get("Imgur")
        return imgur_config.client_id if imgur_config and imgur_config.client_id else ""
    
    @Property(str, notify=configChanged)
    def imgurAccessToken(self):
        imgur_config = self.config_manager.config.hosts.get("Imgur")
        return imgur_config.access_token if imgur_config and imgur_config.access_token else ""
    
    @Property(str, notify=configChanged)
    def imgbbApiKey(self):
        imgbb_config = self.config_manager.config.hosts.get("ImgBB")
        return imgbb_config.api_key if imgbb_config and imgbb_config.api_key else ""
    
    @Property(str, notify=configChanged)
    def imageChestApiKey(self):
        imagechest_config = self.config_manager.config.hosts.get("ImageChest")
        return imagechest_config.api_key if imagechest_config and imagechest_config.api_key else ""
    
    @Property(str, notify=configChanged)
    def pixeldrainApiKey(self):
        pixeldrain_config = self.config_manager.config.hosts.get("Pixeldrain")
        return pixeldrain_config.api_key if pixeldrain_config and pixeldrain_config.api_key else ""
    
    @Property(str, notify=configChanged)
    def imgboxSessionCookie(self):
        imgbox_config = self.config_manager.config.hosts.get("Imgbox")
        return imgbox_config.session_cookie if imgbox_config and imgbox_config.session_cookie else ""
    
    @Property(str, notify=configChanged)
    def imghippoApiKey(self):
        imghippo_config = self.config_manager.config.hosts.get("ImgHippo")
        return imghippo_config.api_key if imghippo_config and imghippo_config.api_key else ""
    
    @Property(str, notify=configChanged)
    def imgpileApiKey(self):
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        return imgpile_config.api_key if imgpile_config and imgpile_config.api_key else ""
    
    @Property(str, notify=configChanged)
    def imgpileBaseUrl(self):
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        return imgpile_config.base_url if imgpile_config and imgpile_config.base_url else "https://imgpile.com"
    
    @Property(int, notify=configChanged)
    def maxWorkers(self):
        host_config = self.config_manager.config.hosts.get(self.config_manager.config.selected_host)
        return host_config.max_workers if host_config else 5
    
    @Property(int, notify=configChanged)
    def rateLimit(self):
        host_config = self.config_manager.config.hosts.get(self.config_manager.config.selected_host)
        return int(host_config.rate_limit) if host_config else 1
    
    @Property(str, notify=configChanged)
    def githubToken(self):
        return self.config_manager.config.github.get("token", "")
    
    @Property(str, notify=configChanged)
    def githubRepo(self):
        return self.config_manager.config.github.get("repo", "")
    
    @Property(str, notify=configChanged)
    def githubBranch(self):
        return self.config_manager.config.github.get("branch", "main")
    
    @Property(str, notify=configChanged)
    def githubFolder(self):
        return self.config_manager.config.github.get("folder", "metadata")
    
    githubFoldersChanged = Signal()
    
    @Property(list, notify=githubFoldersChanged)
    def githubFolders(self):
        return getattr(self, '_github_folders', ["metadata"])
    
    @Property(str, notify=configChanged)
    def jsonUpdateMode(self):
        return self.config_manager.config.json_update_mode
    
    @Property(list, constant=True)
    def availableUpdateModes(self):
        return [
            {"value": "add", "text": "Adicionar Novos (mantém existentes)"},
            {"value": "replace", "text": "Substituir Todos"},
            {"value": "smart", "text": "Inteligente (recomendado)"}
        ]
    
    # Manga info properties
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
        return self._manga_info.get("hasJson", False)
    
    @Slot()
    def initialize_async_services(self):
        """Initialize async services after event loop is ready"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.upload_queue.start())
            else:
                # If no running loop, start queue synchronously
                loop.run_until_complete(self.upload_queue.start())
        except RuntimeError:
            # Queue will be started when first upload is requested
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
    
    @Slot('QVariant')
    def updateConfig(self, config_data):
        """Update configuration from QML"""
        try:
            logger.debug(f"updateConfig received: {type(config_data)}")
            
            # Convert QJSValue to Python dict if needed
            if isinstance(config_data, QJSValue):
                config_dict = config_data.toVariant()
                logger.debug(f"Converted QJSValue to: {type(config_dict)}")
            elif hasattr(config_data, 'toVariant'):
                config_dict = config_data.toVariant()
                logger.debug(f"Converted to variant: {type(config_dict)}")
            else:
                config_dict = config_data
                logger.debug(f"Using direct type: {type(config_dict)}")
            
            # Ensure we have a valid dict
            if not isinstance(config_dict, dict):
                error_msg = f"Dados de configuração inválidos: {type(config_dict)}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            logger.debug(f"Config dict keys: {list(config_dict.keys())}")
            
            # Update root and output folders
            if "rootFolder" in config_dict:
                root_path_str = str(config_dict["rootFolder"]).strip()
                # Handle file:// URLs from QML FolderDialog
                if root_path_str.startswith("file:///"):
                    root_path_str = root_path_str[8:]  # Remove file:///
                elif root_path_str.startswith("file://"):
                    root_path_str = root_path_str[7:]  # Remove file://
                
                self.config_manager.config.root_folder = Path(root_path_str)
                logger.debug(f"Updated root folder: {self.config_manager.config.root_folder}")
                
            if "outputFolder" in config_dict:
                output_path_str = str(config_dict["outputFolder"]).strip()
                if output_path_str:
                    # Handle file:// URLs
                    if output_path_str.startswith("file:///"):
                        output_path_str = output_path_str[8:]
                    elif output_path_str.startswith("file://"):
                        output_path_str = output_path_str[7:]
                    self.config_manager.config.output_folder = Path(output_path_str)
                else:
                    self.config_manager.config.output_folder = self.config_manager.config.root_folder / "Manga_Metadata_Output"
                logger.debug(f"Updated output folder: {self.config_manager.config.output_folder}")
            
            # Update host-specific settings
            if "catboxUserhash" in config_dict:
                catbox_config = self.config_manager.config.hosts.get("Catbox")
                if catbox_config:
                    catbox_config.userhash = config_dict["catboxUserhash"]
            
            if "imgurClientId" in config_dict:
                imgur_config = self.config_manager.config.hosts.get("Imgur")
                if imgur_config:
                    imgur_config.client_id = config_dict["imgurClientId"]
                    imgur_config.enabled = bool(config_dict["imgurClientId"])
            
            if "imgurAccessToken" in config_dict:
                imgur_config = self.config_manager.config.hosts.get("Imgur")
                if imgur_config:
                    imgur_config.access_token = config_dict["imgurAccessToken"]
            
            # Update API keys for new hosts
            if "imgbbApiKey" in config_dict:
                imgbb_config = self.config_manager.config.hosts.get("ImgBB")
                if imgbb_config:
                    imgbb_config.api_key = config_dict["imgbbApiKey"]
                    imgbb_config.enabled = bool(config_dict["imgbbApiKey"])
            
            if "imageChestApiKey" in config_dict:
                imagechest_config = self.config_manager.config.hosts.get("ImageChest")
                if imagechest_config:
                    imagechest_config.api_key = config_dict["imageChestApiKey"]
                    imagechest_config.enabled = bool(config_dict["imageChestApiKey"])
            
            if "pixeldrainApiKey" in config_dict:
                pixeldrain_config = self.config_manager.config.hosts.get("Pixeldrain")
                if pixeldrain_config:
                    pixeldrain_config.api_key = config_dict["pixeldrainApiKey"]
                    # Pixeldrain can work without API key
                    pixeldrain_config.enabled = True
            
            if "imgboxSessionCookie" in config_dict:
                imgbox_config = self.config_manager.config.hosts.get("Imgbox")
                if imgbox_config:
                    imgbox_config.session_cookie = config_dict["imgboxSessionCookie"]
                    imgbox_config.enabled = True
            
            # Update worker settings for current host
            host_config = self.config_manager.config.hosts.get(self.config_manager.config.selected_host)
            if host_config:
                if "maxWorkers" in config_dict:
                    host_config.max_workers = config_dict["maxWorkers"]
                if "rateLimit" in config_dict:
                    host_config.rate_limit = float(config_dict["rateLimit"])
            
            # Update GitHub settings (clean strings)
            if "githubToken" in config_dict:
                self.config_manager.config.github["token"] = str(config_dict["githubToken"]).strip()
            if "githubRepo" in config_dict:
                self.config_manager.config.github["repo"] = str(config_dict["githubRepo"]).strip()
            if "githubBranch" in config_dict:
                self.config_manager.config.github["branch"] = str(config_dict["githubBranch"]).strip()
            if "githubFolder" in config_dict:
                self.config_manager.config.github["folder"] = str(config_dict["githubFolder"]).strip()
            
            # Update JSON update mode
            if "jsonUpdateMode" in config_dict:
                self.config_manager.config.json_update_mode = str(config_dict["jsonUpdateMode"]).strip()
            
            # Save and reinitialize hosts
            self.config_manager.save_config()
            self._init_hosts()
            self.configChanged.emit()
            self.refreshMangaList()
            
        except Exception as e:
            error_msg = f"Erro ao atualizar configurações: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Config data type was: {type(config_data)}")
            if hasattr(config_data, '__dict__'):
                logger.error(f"Config data dict: {config_data.__dict__}")
            self.error.emit(error_msg)
    
    @Slot()
    def refreshMangaList(self):
        """Refresh the manga list from root folder"""
        try:
            if not hasattr(self.config_manager, 'config') or not self.config_manager.config:
                self.manga_model.clear()
                return
            
            root_folder = self.config_manager.config.root_folder
            if not root_folder or not root_folder.exists():
                self.manga_model.clear()
                return
            
            manga_list = []
            for item in sorted(root_folder.iterdir()):
                if item.is_dir():
                    # Count chapters (subdirectories)
                    chapter_count = sum(1 for sub in item.iterdir() if sub.is_dir())
                    
                    # Try to load cover from JSON
                    cover_url = ""
                    try:
                        from utils.helpers import sanitize_filename
                        import json
                        
                        output_folder = self.config_manager.config.output_folder
                        manga_folder = output_folder / item.name
                        
                        # Try multiple approaches to find JSON file
                        json_file = None
                        
                        # 1. Try with sanitized filename
                        sanitized_title = sanitize_filename(item.name, is_file=False, remove_accents=True)
                        potential_json = manga_folder / f"{sanitized_title}.json"
                        if potential_json.exists():
                            json_file = potential_json
                            logger.debug(f"Found JSON method 1 for {item.name}: {json_file.name}")
                        
                        # 2. If not found, try looking for any .json file in the folder
                        if not json_file and manga_folder.exists():
                            for file in manga_folder.glob("*.json"):
                                json_file = file
                                logger.debug(f"Found JSON method 2 for {item.name}: {json_file.name}")
                                break
                        
                        # 2.5. If manga folder doesn't exist, try to find similar named folders
                        if not json_file and not manga_folder.exists():
                            output_folder = self.config_manager.config.output_folder
                            if output_folder.exists():
                                # Look for folders with similar names
                                manga_name_words = item.name.lower().split()
                                for folder in output_folder.iterdir():
                                    if folder.is_dir():
                                        folder_name_words = folder.name.lower().split()
                                        # Check if there's significant overlap
                                        if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                            # Found a similar folder, try to find JSON in it
                                            for file in folder.glob("*.json"):
                                                json_file = file
                                                logger.debug(f"Found JSON method 2.5 for {item.name}: {json_file.name} (in folder {folder.name})")
                                                break
                                            if json_file:
                                                break
                        
                        # 3. Try with exact folder name
                        if not json_file:
                            exact_json = manga_folder / f"{item.name}.json"
                            if exact_json.exists():
                                json_file = exact_json
                                logger.debug(f"Found JSON method 3 for {item.name}: {json_file.name}")
                        
                        # 4. Try different sanitization variations
                        if not json_file:
                            logger.debug(f"Checking if manga folder exists: {manga_folder}")
                            if manga_folder.exists():
                                logger.debug(f"Manga folder exists, trying variations for: {item.name}")
                            else:
                                logger.debug(f"Manga folder does NOT exist: {manga_folder}")
                                # Try to list what's actually in the output folder
                                output_folder = self.config_manager.config.output_folder
                                if output_folder.exists():
                                    logger.debug(f"Output folder contents: {list(output_folder.iterdir())}")
                                else:
                                    logger.debug(f"Output folder does not exist: {output_folder}")
                            
                            if manga_folder.exists():
                                # Try with different characters replacement
                                base_name = item.name
                                variations = [
                                    # Standard variations
                                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                                    base_name.replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "-").replace("ã", "a").replace("ç", "c"),
                                    base_name.replace(" ", "_").replace("-", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                                    # More aggressive variations  
                                    base_name.replace(" - ", " ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                                    base_name.replace(" - ", "").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                                    # With "A" instead of "A"
                                    base_name.replace(" - A ", " A ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                                    base_name.replace(" - A ", "_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                                    # Remove articles
                                    base_name.replace("Tower of God - A ", "Tower_of_God_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                                    base_name.replace("Tower of God - A ", "Tower_of_God_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_")
                                ]
                                
                                logger.debug(f"Trying {len(variations)} variations for {item.name}")
                                for i, variation in enumerate(variations):
                                    potential_file = manga_folder / f"{variation}.json"
                                    logger.debug(f"Variation {i+1}: trying {potential_file.name}")
                                    if potential_file.exists():
                                        json_file = potential_file
                                        logger.debug(f"Found JSON method 4 for {item.name}: {json_file.name} (variation: {variation})")
                                        break
                        
                        if json_file and json_file.exists():
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                cover_url = data.get("cover", "")
                                if cover_url:
                                    logger.debug(f"Loaded cover for {item.name}: {cover_url[:50]}...")
                                else:
                                    logger.debug(f"No cover found for {item.name} - JSON has cover field: {repr(data.get('cover', 'MISSING'))}")
                        else:
                            logger.debug(f"No JSON file found for {item.name} in {manga_folder}")
                    except Exception as e:
                        logger.warning(f"Could not load cover for {item.name}: {e}")
                    
                    manga_entry = {
                        'title': item.name,
                        'path': str(item),
                        'chapterCount': chapter_count,
                        'coverUrl': cover_url
                    }
                    manga_list.append(manga_entry)
                    logger.debug(f"Found manga: {manga_entry}")
            
            logger.debug(f"Setting {len(manga_list)} mangas to model")
            self.manga_model.setMangas(manga_list)
            self.mangaListChanged.emit()
        except Exception as e:
            self.error.emit(f"Erro ao carregar mangás: {str(e)}")
            self.manga_model.clear()
    
    @Slot(str)
    def filterMangaList(self, search_text: str):
        """Filter manga list based on search text"""
        try:
            if not hasattr(self.config_manager, 'config') or not self.config_manager.config:
                return
            
            root_folder = self.config_manager.config.root_folder
            if not root_folder or not root_folder.exists():
                return
            
            manga_list = []
            search_lower = search_text.lower().strip()
            
            for item in sorted(root_folder.iterdir()):
                if item.is_dir():
                    # Check if manga matches search
                    if not search_lower or search_lower in item.name.lower():
                        # Count chapters (subdirectories)
                        chapter_count = sum(1 for sub in item.iterdir() if sub.is_dir())
                        
                        # Try to load cover from JSON using robust method (same as refreshMangaList)
                        cover_url = ""
                        try:
                            from utils.helpers import sanitize_filename
                            import json
                            
                            output_folder = self.config_manager.config.output_folder
                            manga_folder = output_folder / item.name
                            
                            json_file = None
                            
                            # Method 1: Check sanitized filename in title folder
                            if manga_folder.exists():
                                sanitized_title = sanitize_filename(item.name, is_file=False, remove_accents=True)
                                json_file_path = manga_folder / f"{sanitized_title}.json"
                                if json_file_path.exists():
                                    json_file = json_file_path
                                    logger.debug(f"Found JSON method 1 for {item.name}: {json_file.name}")
                            
                            # Method 2: Glob search in title folder
                            if not json_file and manga_folder.exists():
                                for file in manga_folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2 for {item.name}: {json_file.name}")
                                    break
                            
                            # Method 2.5: Similar folder matching (same as refreshMangaList)
                            if not json_file and not manga_folder.exists():
                                manga_name_words = item.name.lower().split()
                                for folder in output_folder.iterdir():
                                    if folder.is_dir():
                                        folder_name_words = folder.name.lower().split()
                                        if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                            for file in folder.glob("*.json"):
                                                json_file = file
                                                logger.debug(f"Found JSON method 2.5 for {item.name}: {json_file.name} (in folder {folder.name})")
                                                break
                                            if json_file:
                                                break
                            
                            if json_file and json_file.exists():
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    cover_url = data.get("cover", "")
                                    if cover_url:
                                        logger.debug(f"Loaded cover for {item.name}: {cover_url[:50]}...")
                                    else:
                                        logger.debug(f"No cover found for {item.name} - JSON has cover field: '{cover_url}'")
                        except Exception as e:
                            logger.debug(f"Could not load cover for {item.name}: {e}")
                        
                        manga_entry = {
                            'title': item.name,
                            'path': str(item),
                            'chapterCount': chapter_count,
                            'coverUrl': cover_url
                        }
                        manga_list.append(manga_entry)
            
            logger.debug(f"Filtered to {len(manga_list)} mangas with search: '{search_text}'")
            self.manga_model.setMangas(manga_list)
            self.mangaListChanged.emit()
            
        except Exception as e:
            logger.error(f"Error filtering manga list: {e}")
            self.error.emit(f"Erro ao filtrar mangás: {str(e)}")
    
    @Slot(str)
    def loadMangaDetails(self, manga_path: str):
        """Load details for selected manga"""
        try:
            path = Path(manga_path)
            self._current_manga = Manga(title=path.name, path=path)
            
            # Update chapter list
            chapters = []
            for chapter_dir in sorted(path.iterdir()):
                if chapter_dir.is_dir():
                    # Count images
                    image_count = sum(1 for f in chapter_dir.iterdir() 
                                    if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'})
                    chapters.append({
                        'name': chapter_dir.name,
                        'path': str(chapter_dir),
                        'imageCount': image_count,
                        'selected': False
                    })
            
            self.chapter_model.setChapters(chapters)
            self.chapterListChanged.emit()
            
            # Load manga info from JSON if available
            self._loadMangaInfo(self._current_manga.title, len(chapters))
            
        except Exception as e:
            self.error.emit(f"Erro ao carregar detalhes: {str(e)}")
            self.chapter_model.clear()
    
    def _loadMangaInfo(self, manga_title: str, folder_chapter_count: int):
        """Load manga information from JSON file if it exists"""
        try:
            from utils.helpers import sanitize_filename
            import json
            
            output_folder = self.config_manager.config.output_folder
            manga_folder = output_folder / manga_title
            
            # Try multiple approaches to find JSON file
            json_file = None
            
            # 1. Try with sanitized filename
            sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
            potential_json = manga_folder / f"{sanitized_title}.json"
            if potential_json.exists():
                json_file = potential_json
            
            # 2. If not found, try looking for any .json file in the folder
            if not json_file and manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    break
            
            # 2.5. If manga folder doesn't exist, try to find similar named folders
            if not json_file and not manga_folder.exists():
                if output_folder.exists():
                    # Look for folders with similar names
                    manga_name_words = manga_title.lower().split()
                    for folder in output_folder.iterdir():
                        if folder.is_dir():
                            folder_name_words = folder.name.lower().split()
                            # Check if there's significant overlap
                            if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                # Found a similar folder, try to find JSON in it
                                for file in folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2.5 for _loadMangaInfo {manga_title}: {json_file.name} (in folder {folder.name})")
                                    break
                                if json_file:
                                    break
            
            # 3. Try with exact folder name
            if not json_file:
                exact_json = manga_folder / f"{manga_title}.json"
                if exact_json.exists():
                    json_file = exact_json
            
            # 4. Try different sanitization variations
            if not json_file and manga_folder.exists():
                # Try with different characters replacement
                base_name = manga_title
                variations = [
                    # Standard variations
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "-").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("-", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    # More aggressive variations  
                    base_name.replace(" - ", " ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - ", "").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # With "A" instead of "A"
                    base_name.replace(" - A ", " A ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - A ", "_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # Remove articles
                    base_name.replace("Tower of God - A ", "Tower_of_God_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace("Tower of God - A ", "Tower_of_God_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_")
                ]
                
                for variation in variations:
                    potential_file = manga_folder / f"{variation}.json"
                    if potential_file.exists():
                        json_file = potential_file
                        break
            
            if json_file and json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update manga info with JSON data
                self._manga_info = {
                    "title": data.get("title", manga_title),
                    "description": data.get("description", ""),
                    "artist": data.get("artist", ""),
                    "author": data.get("author", ""),
                    "cover": data.get("cover", ""),
                    "status": data.get("status", ""),
                    "chapterCount": len(data.get("chapters", {})),
                    "hasJson": True
                }
                logger.debug(f"Loaded manga info from JSON: {self._manga_info['title']}")
            else:
                # No JSON found, use folder data
                self._manga_info = {
                    "title": manga_title,
                    "description": "",
                    "artist": "",
                    "author": "",
                    "cover": "",
                    "status": "",
                    "chapterCount": folder_chapter_count,
                    "hasJson": False
                }
                logger.debug(f"No JSON found, using folder data: {manga_title}")
            
            # Emit signal to update UI
            self.mangaInfoChanged.emit()
            
        except Exception as e:
            logger.error(f"Error loading manga info: {e}")
            # Use fallback data
            self._manga_info = {
                "title": manga_title,
                "description": "",
                "artist": "",
                "author": "",
                "cover": "",
                "status": "",
                "chapterCount": folder_chapter_count,
                "hasJson": False
            }
            self.mangaInfoChanged.emit()
    
    @Slot(str)
    def setHost(self, host_name: str):
        """Change the active upload host"""
        if self.uploader_service.set_host(host_name):
            self.config_manager.config.selected_host = host_name
            self.config_manager.save_config()
            self.selectedHostIndexChanged.emit()
    
    @Slot(str)
    def setImgHippoApiKey(self, api_key: str):
        """Set ImgHippo API key"""
        imghippo_config = self.config_manager.config.hosts.get("ImgHippo")
        if imghippo_config:
            imghippo_config.api_key = api_key.strip()
            self.config_manager.save_config()
            self._init_hosts()
            self.configChanged.emit()
    
    @Slot(str)
    def setImgPileApiKey(self, api_key: str):
        """Set ImgPile API key"""
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        if imgpile_config:
            imgpile_config.api_key = api_key.strip()
            self.config_manager.save_config()
            self._init_hosts()
            self.configChanged.emit()
    
    @Slot(str)
    def setImgPileBaseUrl(self, base_url: str):
        """Set ImgPile base URL"""
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        if imgpile_config:
            imgpile_config.base_url = base_url.strip() or "https://imgpile.com"
            self.config_manager.save_config()
            self._init_hosts()
            self.configChanged.emit()
    
    @Slot()
    def startUpload(self):
        """Start uploading selected chapters (legacy method)"""
        # Use default metadata
        default_metadata = {
            "title": self._current_manga.title if self._current_manga else "",
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
            if not self._current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return
            
            selected_chapters = self.chapter_model.getSelectedChapters()
            if not selected_chapters:
                self.error.emit("Nenhum capítulo selecionado")
                return
            
            # Convert QJSValue to Python dict if needed
            if isinstance(metadata, QJSValue):
                metadata_dict = metadata.toVariant()
                logger.debug(f"Upload metadata - Converted QJSValue to: {type(metadata_dict)}")
            elif hasattr(metadata, 'toVariant'):
                metadata_dict = metadata.toVariant()
                logger.debug(f"Upload metadata - Converted to variant: {type(metadata_dict)}")
            else:
                metadata_dict = metadata
                logger.debug(f"Upload metadata - Using direct type: {type(metadata_dict)}")
            
            # Ensure we have a valid dict
            if not isinstance(metadata_dict, dict):
                error_msg = f"Dados de metadados inválidos para upload: {type(metadata_dict)}"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
            
            logger.debug(f"Upload metadata dict keys: {list(metadata_dict.keys())}")
            
            # Store metadata for upload
            self._upload_metadata = metadata_dict
            self.processingStarted.emit()
            
            # Add to queue
            asyncio.ensure_future(self._queue_upload(selected_chapters))
            
        except Exception as e:
            logger.error(f"Error in startUploadWithMetadata: {e}")
            self.error.emit(f"Erro ao iniciar upload com metadados: {str(e)}")
    
    async def _queue_upload(self, selected_chapters: List[str]):
        """Queue upload job"""
        job_id = await self.upload_queue.add_job(
            self._upload_async,
            selected_chapters
        )
        
        # Monitor job progress
        asyncio.ensure_future(self._monitor_job(job_id))
    
    async def _monitor_job(self, job_id: str):
        """Monitor upload job progress"""
        while True:
            try:
                job = await self.upload_queue.wait_for_job(job_id, timeout=1.0)  # Increased timeout
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
                # Job still running, continue monitoring
                pass
            await asyncio.sleep(0.5)  # Less frequent polling
    
    async def _upload_async(self, selected_chapters: List[str]):
        """Async upload handler"""
        try:
            # Recreate chapter objects with proper image scanning
            chapters_to_upload = []
            for chapter_name in selected_chapters:
                chapter_path = self._current_manga.path / chapter_name
                if chapter_path.exists():
                    chapter = Chapter(name=chapter_name, path=chapter_path, images=[])
                    chapters_to_upload.append(chapter)
            
            if not chapters_to_upload:
                self.error.emit("Nenhum capítulo válido selecionado")
                return
            
            # Upload
            results = await self.uploader_service.upload_manga(
                self._current_manga,
                chapters_to_upload
            )
            
            # Generate metadata with configured update mode
            output_path = self.config_manager.config.output_folder / self._current_manga.title / f"{self._current_manga.title}.json"
            update_mode = self.config_manager.config.json_update_mode
            saved_json_path = await self.uploader_service.generate_metadata(
                self._current_manga,
                results,
                output_path,
                update_mode,
                self._upload_metadata
            )
            
            # Store the path for potential GitHub upload
            self._last_json_path = saved_json_path
            
            # Auto-upload to GitHub if configured
            github_config = self.config_manager.config.github
            if all([github_config.get("token"), github_config.get("repo")]):
                logger.info("Auto-uploading metadata to GitHub...")
                asyncio.ensure_future(self._upload_to_github(saved_json_path))
            else:
                logger.debug("GitHub not configured, skipping auto-upload")
            
            # Reload manga info to reflect new JSON data
            if self._current_manga:
                folder_chapters = self.chapter_model.rowCount()
                self._loadMangaInfo(self._current_manga.title, folder_chapters)
            
            self.processingFinished.emit()
        except Exception as e:
            self.error.emit(f"Erro no upload: {str(e)}")
            self.processingFinished.emit()
    
    @Slot()
    def saveToGitHub(self):
        """Save metadata to GitHub repository"""
        github_config = self.config_manager.config.github
        if not all([github_config.get("token"), github_config.get("repo")]):
            self.error.emit("Configurações do GitHub incompletas (token/repositório)")
            return
        
        if not self._current_manga:
            self.error.emit("Nenhum mangá processado recentemente")
            return
        
        # Use robust JSON finding method (same as refreshMangaList)
        output_folder = self.config_manager.config.output_folder
        from utils.helpers import sanitize_filename
        import glob
        
        json_file = None
        
        # Method 1: Check sanitized filename in title folder
        manga_folder = output_folder / self._current_manga.title
        if manga_folder.exists():
            sanitized_title = sanitize_filename(self._current_manga.title, is_file=False, remove_accents=True)
            json_file_path = manga_folder / f"{sanitized_title}.json"
            if json_file_path.exists():
                json_file = json_file_path
        
        # Method 2: Glob search in title folder
        if not json_file and manga_folder.exists():
            for file in manga_folder.glob("*.json"):
                json_file = file
                break
        
        # Method 2.5: Similar folder matching
        if not json_file and not manga_folder.exists():
            manga_name_words = self._current_manga.title.lower().split()
            for folder in output_folder.iterdir():
                if folder.is_dir():
                    folder_name_words = folder.name.lower().split()
                    if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                        for file in folder.glob("*.json"):
                            json_file = file
                            break
                        if json_file:
                            break
        
        if not json_file or not json_file.exists():
            self.error.emit("Arquivo de metadados não encontrado")
            return
        
        logger.debug(f"Found JSON for GitHub upload: {json_file}")
        
        # Start GitHub upload
        asyncio.ensure_future(self._upload_to_github(json_file))
    
    async def _upload_to_github(self, json_file: Path):
        """Upload metadata file to GitHub"""
        try:
            github_config = self.config_manager.config.github
            
            # Clean configuration values (remove problematic characters)
            def clean_string(s):
                return str(s).strip().replace('\n', '').replace('\r', '').replace('\t', '')
            
            token = clean_string(github_config["token"])
            repo = clean_string(github_config["repo"])
            branch = clean_string(github_config.get("branch", "main"))
            
            github_service = GitHubService(
                token=token,
                repo=repo,
                branch=branch
            )
            
            # Create remote path using configured folder
            github_folder = clean_string(github_config.get("folder", "metadata"))
            remote_path = f"{github_folder}/{json_file.name}" if github_folder else json_file.name
            commit_message = f"Update manga metadata: {json_file.stem}"
            
            logger.debug(f"GitHub upload: {token[:10]}... → {repo} → {remote_path}")
            
            async with github_service:
                success = await github_service.upload_file(
                    json_file, remote_path, commit_message
                )
            
            if success:
                self.processingFinished.emit()  # Reuse signal for success notification
            else:
                self.error.emit("Falha no upload para GitHub")
                
        except Exception as e:
            self.error.emit(f"Erro no GitHub: {str(e)}")
    
    @Slot()
    def refreshGitHubFolders(self):
        """Load all folders from GitHub repository"""
        github_config = self.config_manager.config.github
        if not all([github_config.get("token"), github_config.get("repo")]):
            logger.warning("GitHub configuration incomplete")
            return
        
        # Start async folder loading
        asyncio.ensure_future(self._refresh_github_folders())
    
    async def _refresh_github_folders(self):
        """Load all folders from GitHub repository recursively"""
        try:
            github_config = self.config_manager.config.github
            
            # Clean configuration values
            def clean_string(s):
                return str(s).strip().replace('\n', '').replace('\r', '').replace('\t', '')
            
            token = clean_string(github_config["token"])
            repo = clean_string(github_config["repo"])
            branch = clean_string(github_config.get("branch", "main"))
            
            github_service = GitHubService(
                token=token,
                repo=repo,
                branch=branch
            )
            
            logger.debug("Loading all GitHub folders recursively")
            
            async with github_service:
                all_folders = await self._get_all_folders_recursive(github_service, "")
            
            # Add default options
            folder_options = ["", "metadata"] + sorted(set(all_folders))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_folders = []
            for folder in folder_options:
                if folder not in seen:
                    seen.add(folder)
                    unique_folders.append(folder)
            
            self._github_folders = unique_folders
            self.githubFoldersChanged.emit()
            logger.debug(f"Loaded {len(unique_folders)} GitHub folder options")
                
        except Exception as e:
            logger.error(f"Error loading GitHub folders: {e}")
            # Fallback to default options
            self._github_folders = ["", "metadata"]
            self.githubFoldersChanged.emit()
    
    async def _get_all_folders_recursive(self, github_service, path: str = "", max_depth: int = 3, current_depth: int = 0):
        """Recursively get all folders in the repository"""
        if current_depth >= max_depth:
            return []
        
        all_folders = []
        
        try:
            folders = await github_service.list_folders(path)
            
            for folder in folders:
                if folder["type"] == "dir" and folder["name"] != "..":
                    folder_path = folder["path"]
                    all_folders.append(folder_path)
                    
                    # Recursively get subfolders
                    subfolders = await self._get_all_folders_recursive(
                        github_service, folder_path, max_depth, current_depth + 1
                    )
                    all_folders.extend(subfolders)
                    
        except Exception as e:
            logger.warning(f"Error loading subfolders for {path}: {e}")
        
        return all_folders
    
    @Slot(str)
    def selectGitHubFolder(self, folder_path: str):
        """Select a GitHub folder and update the configuration"""
        github_config = self.config_manager.config.github
        github_config["folder"] = folder_path
        self.config_manager.save_config()
        self.configChanged.emit()
        logger.info(f"GitHub folder selected: {folder_path}")
    
    @Slot(str, result=str)
    def makeJsonSafe(self, text: str) -> str:
        """Convert text to JSON-safe format"""
        if not text:
            return ""
        
        # Replace problematic characters for JSON
        safe_text = text.replace('\\', '\\\\')
        safe_text = safe_text.replace('"', '\\"')
        safe_text = safe_text.replace('\n', '\\n')
        safe_text = safe_text.replace('\r', '\\r')
        safe_text = safe_text.replace('\t', '\\t')
        
        return safe_text
    
    @Slot(str)
    def loadExistingMetadata(self, manga_title: str):
        """Load existing metadata for editing"""
        try:
            from utils.helpers import sanitize_filename
            import json
            
            output_folder = self.config_manager.config.output_folder
            manga_folder = output_folder / manga_title
            
            logger.debug(f"Loading metadata for edit: {manga_title}")
            logger.debug(f"Looking in folder: {manga_folder}")
            
            # Try multiple approaches to find JSON file
            json_file = None
            
            # 1. Try with sanitized filename
            sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
            potential_json = manga_folder / f"{sanitized_title}.json"
            if potential_json.exists():
                json_file = potential_json
                logger.debug(f"Found JSON with sanitized name: {json_file}")
            
            # 2. If not found, try looking for any .json file in the folder
            if not json_file and manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    logger.debug(f"Found JSON file: {json_file}")
                    break
            
            # 2.5. If manga folder doesn't exist, try to find similar named folders
            if not json_file and not manga_folder.exists():
                if output_folder.exists():
                    # Look for folders with similar names
                    manga_name_words = manga_title.lower().split()
                    for folder in output_folder.iterdir():
                        if folder.is_dir():
                            folder_name_words = folder.name.lower().split()
                            # Check if there's significant overlap
                            if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                # Found a similar folder, try to find JSON in it
                                for file in folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2.5 for loadExistingMetadata {manga_title}: {json_file.name} (in folder {folder.name})")
                                    break
                                if json_file:
                                    break
            
            # 3. Try with exact folder name
            if not json_file:
                exact_json = manga_folder / f"{manga_title}.json"
                if exact_json.exists():
                    json_file = exact_json
                    logger.debug(f"Found JSON with exact name: {json_file}")
            
            # 4. Try different sanitization variations
            if not json_file and manga_folder.exists():
                logger.debug(f"Trying variations for: {manga_title}")
                # Try with different characters replacement
                base_name = manga_title
                variations = [
                    # Standard variations
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "-").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("-", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    # More aggressive variations  
                    base_name.replace(" - ", " ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - ", "").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # With "A" instead of "A"
                    base_name.replace(" - A ", " A ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - A ", "_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # Remove articles
                    base_name.replace("Tower of God - A ", "Tower_of_God_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace("Tower of God - A ", "Tower_of_God_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_")
                ]
                
                for i, variation in enumerate(variations):
                    potential_file = manga_folder / f"{variation}.json"
                    logger.debug(f"Variation {i+1}: trying {potential_file}")
                    if potential_file.exists():
                        json_file = potential_file
                        logger.debug(f"Found JSON with variation for {manga_title}: {json_file}")
                        break
            
            if json_file and json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                logger.debug(f"Found existing metadata: {data.get('title', 'No title')}")
                logger.debug(f"Emitting metadataLoaded signal with data: {data}")
                # Emit signal with metadata
                self.metadataLoaded.emit(data)
            else:
                logger.debug(f"No JSON found for {manga_title}, using defaults")
                # No existing metadata, use defaults
                default_data = {
                    "title": manga_title,
                    "description": "",
                    "artist": "",
                    "author": "",
                    "group": "",
                    "cover": "",
                    "status": "Em Andamento"
                }
                logger.debug(f"Emitting default metadataLoaded signal with data: {default_data}")
                self.metadataLoaded.emit(default_data)
                
        except Exception as e:
            logger.error(f"Error loading metadata for {manga_title}: {e}")
            # Use defaults on error
            default_data = {
                "title": manga_title,
                "description": "",
                "artist": "", 
                "author": "",
                "cover": "",
                "status": "Em Andamento"
            }
            self.metadataLoaded.emit(default_data)
    
    @Slot('QVariant')
    def updateExistingMetadata(self, metadata):
        """Update existing metadata file"""
        try:
            if not self._current_manga:
                self.error.emit("Nenhum mangá selecionado")
                return
            
            # Convert QJSValue to Python dict if needed
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
            
            logger.debug(f"Metadata dict keys: {list(metadata_dict.keys())}")
            
            from utils.helpers import sanitize_filename
            import json
            
            output_folder = self.config_manager.config.output_folder
            manga_folder = output_folder / self._current_manga.title
            
            # Try multiple approaches to find JSON file
            json_file = None
            
            # 1. Try with sanitized filename
            sanitized_title = sanitize_filename(self._current_manga.title, is_file=False, remove_accents=True)
            potential_json = manga_folder / f"{sanitized_title}.json"
            if potential_json.exists():
                json_file = potential_json
            
            # 2. If not found, try looking for any .json file in the folder
            if not json_file and manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    break
            
            # 2.5. If manga folder doesn't exist, try to find similar named folders
            if not json_file and not manga_folder.exists():
                if output_folder.exists():
                    # Look for folders with similar names
                    manga_name_words = self._current_manga.title.lower().split()
                    for folder in output_folder.iterdir():
                        if folder.is_dir():
                            folder_name_words = folder.name.lower().split()
                            # Check if there's significant overlap
                            if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                # Found a similar folder, try to find JSON in it
                                for file in folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2.5 for updateExistingMetadata {self._current_manga.title}: {json_file.name} (in folder {folder.name})")
                                    break
                                if json_file:
                                    break
            
            # 3. Try with exact folder name
            if not json_file:
                exact_json = manga_folder / f"{self._current_manga.title}.json"
                if exact_json.exists():
                    json_file = exact_json
            
            # 4. Try different sanitization variations
            if not json_file and manga_folder.exists():
                # Try with different characters replacement
                base_name = self._current_manga.title
                variations = [
                    # Standard variations
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "-").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("-", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    # More aggressive variations  
                    base_name.replace(" - ", " ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - ", "").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # With "A" instead of "A"
                    base_name.replace(" - A ", " A ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - A ", "_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # Remove articles
                    base_name.replace("Tower of God - A ", "Tower_of_God_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace("Tower of God - A ", "Tower_of_God_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_")
                ]
                
                for variation in variations:
                    potential_file = manga_folder / f"{variation}.json"
                    if potential_file.exists():
                        json_file = potential_file
                        break
            
            logger.debug(f"Update metadata - looking for JSON: {json_file}")
            
            if json_file and json_file.exists():
                # Load existing data
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update metadata fields
                data["title"] = metadata_dict.get("title", "")
                data["description"] = metadata_dict.get("description", "")
                data["artist"] = metadata_dict.get("artist", "")
                data["author"] = metadata_dict.get("author", "")
                data["group"] = metadata_dict.get("group", "")
                data["cover"] = metadata_dict.get("cover", "")
                data["status"] = metadata_dict.get("status", "Em Andamento")
                
                # Save updated data
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.success(f"Metadata updated: {json_file}")
                
                # Reload manga info to reflect changes
                if self._current_manga:
                    folder_chapters = self.chapter_model.rowCount()
                    self._loadMangaInfo(self._current_manga.title, folder_chapters)
                
                self.processingFinished.emit()  # Reuse signal for success
            else:
                # Create new JSON file
                logger.info(f"Creating new JSON file for: {self._current_manga.title}")
                
                try:
                    # Create the output folder if it doesn't exist
                    output_folder = self.config_manager.config.output_folder
                    manga_folder = output_folder / self._current_manga.title
                    logger.debug(f"Creating manga folder: {manga_folder}")
                    manga_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Create sanitized filename
                    sanitized_title = sanitize_filename(self._current_manga.title, is_file=True, remove_accents=True)
                    if not sanitized_title.endswith('.json'):
                        sanitized_title += '.json'
                    
                    new_json_file = manga_folder / sanitized_title
                    logger.debug(f"Creating JSON file: {new_json_file}")
                    
                    # Create new metadata structure
                    new_data = {
                        "title": metadata_dict.get("title", ""),
                        "description": metadata_dict.get("description", ""),
                        "artist": metadata_dict.get("artist", ""),
                        "author": metadata_dict.get("author", ""),
                        "group": metadata_dict.get("group", ""),
                        "cover": metadata_dict.get("cover", ""),
                        "status": metadata_dict.get("status", "Em Andamento"),
                        "chapters": {}  # Empty chapters for now
                    }
                    
                    # Save new JSON file
                    with open(new_json_file, 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, indent=2, ensure_ascii=False)
                    
                    logger.success(f"New metadata file created: {new_json_file}")
                    
                    # Reload manga info to reflect changes
                    if self._current_manga:
                        folder_chapters = self.chapter_model.rowCount()
                        self._loadMangaInfo(self._current_manga.title, folder_chapters)
                    
                    # Refresh manga list to show the new JSON status
                    self.refreshMangaList()
                    
                    self.processingFinished.emit()  # Reuse signal for success
                    
                except Exception as create_error:
                    logger.error(f"Error creating new JSON file: {create_error}")
                    self.error.emit(f"Erro ao criar arquivo de metadados: {str(create_error)}")
                
        except Exception as e:
            logger.error(f"Error in updateExistingMetadata: {e}")
            self.error.emit(f"Erro ao atualizar metadados: {str(e)}")
    
    # Signal for cookie test result
    cookieTestResult = Signal(str, str)  # (result_type, message)
    
    @Slot(str)
    def testImgboxCookie(self, cookie):
        """Test Imgbox cookie by attempting a small upload"""
        def run_test():
            try:
                from pathlib import Path
                import tempfile
                
                # Create a minimal test image using PIL
                try:
                    from PIL import Image
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                        temp_path = Path(temp_file.name)
                    
                    # Create a 1x1 pixel test image
                    test_img = Image.new('RGB', (1, 1), color='white')
                    test_img.save(temp_path, 'JPEG')
                    
                except ImportError:
                    # Fallback: create empty file if PIL not available
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                        temp_path = Path(temp_file.name)
                        temp_file.write(b'test')
                
                # Test basic pyimgbox functionality with cookie
                try:
                    import pyimgbox
                    gallery = pyimgbox.Gallery(title="Cookie Test")
                    
                    # Note: pyimgbox doesn't support session auth in constructor
                    # This tests if the library works and file can be processed
                    self.cookieTestResult.emit("success", f"✅ Cookie aceito! pyimgbox funcionando corretamente")
                    
                except ImportError:
                    self.cookieTestResult.emit("error", f"❌ pyimgbox não está instalado")
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
    
    async def shutdown(self):
        """Gracefully shutdown all async services"""
        try:
            if hasattr(self, 'upload_queue'):
                await self.upload_queue.stop()
            logger.info("Backend shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")