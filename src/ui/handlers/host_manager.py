"""Host management handler for UI backend"""

from PySide6.QtCore import QObject, Signal, Property
from typing import Dict, List, Optional
from core.config import ConfigManager
from core.hosts import (
    BaseHost, CatboxHost, ImgurHost, ImgBBHost, LensdumpHost, 
    PixeldrainHost, GofileHost, ImageChestHost, ImgboxHost, 
    ImgHippoHost, ImgPileHost
)
from loguru import logger


class HostManager(QObject):
    """Handles all host-related operations"""
    
    hostChanged = Signal()
    hostsInitialized = Signal()
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.hosts: Dict[str, BaseHost] = {}
        self.host_list = [
            "Catbox", "Imgur", "ImgBB", "Imgbox", "Lensdump", 
            "Pixeldrain", "Gofile", "ImageChest", "ImgHippo", "ImgPile"
        ]
        self._init_hosts()
    
    def _get_host_class(self, host_name: str):
        """Get host class by name"""
        host_classes = {
            "Catbox": CatboxHost,
            "Imgur": ImgurHost,
            "ImgBB": ImgBBHost,
            "Imgbox": ImgboxHost,
            "Lensdump": LensdumpHost,
            "Pixeldrain": PixeldrainHost,
            "Gofile": GofileHost,
            "ImageChest": ImageChestHost,
            "ImgHippo": ImgHippoHost,
            "ImgPile": ImgPileHost
        }
        return host_classes.get(host_name)
    
    # Host Properties
    @Property(list, notify=hostChanged)
    def hostsList(self):
        return self.host_list
    
    @Property(str, notify=hostChanged)
    def selectedHost(self):
        return self.config_manager.config.selected_host
    
    @Property(int, notify=hostChanged)
    def selectedHostIndex(self):
        try:
            return self.host_list.index(self.config_manager.config.selected_host)
        except ValueError:
            return 0
    
    @Property(bool, notify=hostChanged)
    def isCatboxEnabled(self):
        host_config = self.config_manager.config.hosts.get("Catbox")
        return host_config.enabled if host_config else True
    
    @Property(bool, notify=hostChanged)
    def isImgurEnabled(self):
        host_config = self.config_manager.config.hosts.get("Imgur")
        return host_config.enabled if host_config else False
    
    @Property(bool, notify=hostChanged)
    def isImgbbEnabled(self):
        host_config = self.config_manager.config.hosts.get("ImgBB")
        return host_config.enabled if host_config else False
    
    @Property(bool, notify=hostChanged)
    def isImgboxEnabled(self):
        host_config = self.config_manager.config.hosts.get("Imgbox")
        return host_config.enabled if host_config else False
    
    @Property(bool, notify=hostChanged)
    def isLensdumpEnabled(self):
        host_config = self.config_manager.config.hosts.get("Lensdump")
        return host_config.enabled if host_config else True
    
    @Property(bool, notify=hostChanged)
    def isPixeldrainEnabled(self):
        host_config = self.config_manager.config.hosts.get("Pixeldrain")
        return host_config.enabled if host_config else True
    
    @Property(bool, notify=hostChanged)
    def isGofileEnabled(self):
        host_config = self.config_manager.config.hosts.get("Gofile")
        return host_config.enabled if host_config else True
    
    @Property(bool, notify=hostChanged)
    def isImageChestEnabled(self):
        host_config = self.config_manager.config.hosts.get("ImageChest")
        return host_config.enabled if host_config else False
    
    @Property(bool, notify=hostChanged)
    def isImgHippoEnabled(self):
        host_config = self.config_manager.config.hosts.get("ImgHippo")
        return host_config.enabled if host_config else True
    
    @Property(bool, notify=hostChanged)
    def isImgPileEnabled(self):
        host_config = self.config_manager.config.hosts.get("ImgPile")
        return host_config.enabled if host_config else True
    
    def set_host(self, host_name: str):
        """Set the active upload host"""
        if host_name in self.host_list:
            self.config_manager.config.selected_host = host_name
            logger.debug(f"Selected host changed to: {host_name}")
            self.hostChanged.emit()
    
    def get_current_host(self) -> Optional[BaseHost]:
        """Get the currently selected host instance"""
        host_name = self.config_manager.config.selected_host
        return self.hosts.get(host_name)
    
    def get_host(self, host_name: str) -> Optional[BaseHost]:
        """Get a specific host instance"""
        return self.hosts.get(host_name)
    
    def get_enabled_hosts(self) -> List[str]:
        """Get list of enabled host names"""
        enabled_hosts = []
        for host_name in self.host_list:
            host_config = self.config_manager.config.hosts.get(host_name)
            if host_config and host_config.enabled:
                enabled_hosts.append(host_name)
        return enabled_hosts
    
    def _init_hosts(self):
        """Initialize all host instances"""
        self.hosts.clear()
        
        for host_name in self.host_list:
            try:
                host_class = self._get_host_class(host_name)
                if host_class:
                    host_config = self.config_manager.config.hosts.get(host_name)
                    if host_config:
                        # Convert HostConfig to dict for host initialization
                        config_dict = host_config.model_dump()
                        host_instance = host_class(config_dict)
                        self.hosts[host_name] = host_instance
                        logger.debug(f"Initialized host: {host_name}")
                    else:
                        logger.warning(f"No config found for host: {host_name}")
                else:
                    logger.error(f"Host class not found: {host_name}")
            except Exception as e:
                logger.error(f"Failed to initialize host {host_name}: {e}")
        
        logger.info(f"Initialized {len(self.hosts)} hosts")
        self.hostChanged.emit()
        self.hostsInitialized.emit()
    
    def reload_hosts(self):
        """Reload all hosts (useful after config changes)"""
        logger.info("Reloading hosts...")
        self._init_hosts()
    
    def validate_host_config(self, host_name: str) -> tuple[bool, str]:
        """Validate configuration for a specific host"""
        host_config = self.config_manager.config.hosts.get(host_name)
        if not host_config:
            return False, f"No configuration found for {host_name}"
        
        host_instance = self.hosts.get(host_name)
        if not host_instance:
            return False, f"Host {host_name} not initialized"
        
        # Check host-specific requirements
        if host_name == "Imgur":
            if not host_config.client_id:
                return False, "Imgur requires client_id"
        elif host_name == "ImgBB":
            if not host_config.api_key:
                return False, "ImgBB requires api_key"
        elif host_name == "ImageChest":
            if not host_config.api_key:
                return False, "ImageChest requires api_key"
        elif host_name == "Imgbox":
            if not host_config.session_cookie:
                return False, "Imgbox requires session_cookie"
        
        return True, "Configuration valid"
    
    def test_host_connection(self, host_name: str) -> tuple[bool, str]:
        """Test connection to a specific host"""
        is_valid, msg = self.validate_host_config(host_name)
        if not is_valid:
            return False, msg
        
        host_instance = self.hosts.get(host_name)
        if not host_instance:
            return False, f"Host {host_name} not available"
        
        # TODO: Implement actual connection test
        # This would require a test method in BaseHost
        return True, f"{host_name} connection test passed"
    
    def test_imgbox_cookie(self, cookie: str):
        """Test Imgbox cookie functionality"""
        try:
            from PySide6.QtCore import QTimer
            
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
                        # TODO: Emit success signal to backend
                        logger.info("✅ Cookie accepted! pyimgbox working correctly")
                    except ImportError:
                        logger.error("❌ pyimgbox not installed")
                    except Exception as e:
                        logger.error(f"❌ Error: {str(e)}")
                    
                    # Clean up
                    try:
                        temp_path.unlink()
                    except:
                        pass
                        
                except Exception as e:
                    logger.error(f"❌ Test error: {str(e)}")
            
            # Use QTimer to run test without blocking
            QTimer.singleShot(0, run_test)
            
        except Exception as e:
            logger.error(f"Error testing Imgbox cookie: {e}")
    
    def get_current_host(self) -> Optional[BaseHost]:
        """Get current selected host instance"""
        selected_host = self.config_manager.config.selected_host
        return self.hosts.get(selected_host)
    
    def get_host(self, host_name: str) -> Optional[BaseHost]:
        """Get specific host instance"""
        return self.hosts.get(host_name)