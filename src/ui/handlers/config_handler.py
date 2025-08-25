"""Configuration management handler for UI backend"""

from PySide6.QtCore import QObject, Signal, Property
from pathlib import Path
from core.config import ConfigManager
from loguru import logger


class ConfigHandler(QObject):
    """Handles all configuration-related operations"""
    
    configChanged = Signal()
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
    
    # Configuration Properties
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
        return imgur_config.client_id if imgur_config else ""
    
    @Property(str, notify=configChanged)
    def imgurAccessToken(self):
        imgur_config = self.config_manager.config.hosts.get("Imgur")
        return imgur_config.access_token if imgur_config else ""
    
    @Property(str, notify=configChanged)
    def imgbbApiKey(self):
        imgbb_config = self.config_manager.config.hosts.get("ImgBB")
        return imgbb_config.api_key if imgbb_config else ""
    
    @Property(str, notify=configChanged)
    def imageChestApiKey(self):
        imagechest_config = self.config_manager.config.hosts.get("ImageChest")
        return imagechest_config.api_key if imagechest_config else ""
    
    @Property(str, notify=configChanged)
    def pixeldrainApiKey(self):
        pixeldrain_config = self.config_manager.config.hosts.get("Pixeldrain")
        return pixeldrain_config.api_key if pixeldrain_config else ""
    
    @Property(str, notify=configChanged)
    def imgboxSessionCookie(self):
        imgbox_config = self.config_manager.config.hosts.get("Imgbox")
        return imgbox_config.session_cookie if imgbox_config else ""
    
    @Property(str, notify=configChanged)
    def imghippoApiKey(self):
        imghippo_config = self.config_manager.config.hosts.get("ImgHippo")
        return imghippo_config.api_key if imghippo_config else ""
    
    @Property(str, notify=configChanged)
    def imgpileApiKey(self):
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        return imgpile_config.api_key if imgpile_config else ""
    
    @Property(str, notify=configChanged)
    def imgpileBaseUrl(self):
        imgpile_config = self.config_manager.config.hosts.get("ImgPile")
        return imgpile_config.base_url if imgpile_config else "https://imgpile.com"
    
    @Property(str, notify=configChanged)
    def lensdumpApiKey(self):
        lensdump_config = self.config_manager.config.hosts.get("Lensdump")
        return lensdump_config.api_key if lensdump_config else ""
    
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
    
    @Property(str, notify=configChanged)
    def folderStructure(self):
        return self.config_manager.config.folder_structure
    
    @Property(list, constant=True)
    def availableFolderStructures(self):
        return [
            {"value": "standard", "text": "Padrão (Manga/Capítulo/imagens)", "description": "Cada capítulo em sua própria pasta"},
            {"value": "flat", "text": "Plano (Manga/imagens)", "description": "Todas as imagens diretamente na pasta do manga"},
            {"value": "volume_based", "text": "Por Volume (Manga/Volume/Capítulo/imagens)", "description": "Organizado por volumes e capítulos"},
            {"value": "scan_manga_chapter", "text": "Scan-Manga-Capítulo (Scan/NomeScan/Manga/Capítulo/imagens)", "description": "Estrutura organizada por grupo de scan"},
            {"value": "scan_manga_volume_chapter", "text": "Scan-Manga-Volume-Capítulo (Scan/NomeScan/Manga/Volume/Capítulo/imagens)", "description": "Estrutura organizada por grupo de scan com volumes"}
        ]
    
    @Property(int, notify=configChanged)
    def maxWorkers(self):
        host_config = self.config_manager.config.hosts.get(
            self.config_manager.config.selected_host
        )
        return host_config.max_workers if host_config else 3
    
    @Property(float, notify=configChanged)
    def rateLimit(self):
        host_config = self.config_manager.config.hosts.get(
            self.config_manager.config.selected_host
        )
        return host_config.rate_limit if host_config else 1.0
    
    def update_config(self, config_dict: dict):
        """Update configuration from QML"""
        try:
            logger.debug(f"Config dict keys: {list(config_dict.keys())}")
            
            # Update paths
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
            
            # Update host configurations
            self._update_host_configs(config_dict)
            
            # Update other settings
            if "jsonUpdateMode" in config_dict:
                self.config_manager.config.json_update_mode = str(config_dict["jsonUpdateMode"]).strip()
            
            # Update folder structure
            if "folderStructure" in config_dict:
                structure = str(config_dict["folderStructure"]).strip()
                if structure in ["standard", "flat", "volume_based", "scan_manga_chapter", "scan_manga_volume_chapter"]:
                    self.config_manager.config.folder_structure = structure
            
            # Update selected host
            if "selectedHost" in config_dict:
                selected_host = str(config_dict["selectedHost"]).strip()
                if selected_host:  # Only update if not empty
                    self.config_manager.config.selected_host = selected_host
                    logger.debug(f"Updated selected host: {selected_host}")
            
            # Save configuration
            self.config_manager.save_config()
            self.configChanged.emit()
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            raise
    
    def _clean_file_url(self, path_str: str) -> str:
        """Clean file:// URLs from QML FolderDialog"""
        path_str = str(path_str).strip()
        if path_str.startswith("file:///"):
            path_str = path_str[8:]
        elif path_str.startswith("file://"):
            path_str = path_str[7:]
        
        if path_str and not path_str.startswith('/'):
            path_str = '/' + path_str
        
        return path_str
    
    def _update_host_configs(self, config_dict: dict):
        """Update host-specific configurations"""
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
            "lensdumpApiKey": ("Lensdump", "api_key"),
        }
        
        for config_key, (host_name, attr_name) in host_configs.items():
            if config_key in config_dict:
                host_config = self.config_manager.config.hosts.get(host_name)
                if host_config:
                    setattr(host_config, attr_name, config_dict[config_key])
                    if config_key in ["imgurClientId", "imgbbApiKey", "imageChestApiKey"]:
                        host_config.enabled = bool(config_dict[config_key])
                    elif config_key in ["pixeldrainApiKey", "imgboxSessionCookie", "imghippoApiKey", "imgpileApiKey", "lensdumpApiKey"]:
                        host_config.enabled = True  # These hosts work with or without API keys
                    elif config_key == "imgpileBaseUrl":
                        # Don't change enabled status for base URL
                        pass
        
        # Update worker settings for current host
        if "maxWorkers" in config_dict or "rateLimit" in config_dict:
            current_host = self.config_manager.config.selected_host
            host_config = self.config_manager.config.hosts.get(current_host)
            if host_config:
                if "maxWorkers" in config_dict:
                    host_config.max_workers = config_dict["maxWorkers"]
                if "rateLimit" in config_dict:
                    host_config.rate_limit = float(config_dict["rateLimit"])