import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger


class HostConfig(BaseModel):
    enabled: bool = True
    max_workers: int = Field(default=5, ge=1, le=20)
    rate_limit: float = Field(default=1.0, ge=0)
    # Common fields
    userhash: Optional[str] = ""  # Catbox
    client_id: Optional[str] = ""  # Imgur
    access_token: Optional[str] = ""  # Imgur
    api_key: Optional[str] = ""  # ImgBB, ImageChest, Pixeldrain


class AppConfig(BaseModel):
    root_folder: Path = Path.home() / "Manga"
    output_folder: Path = Path.home() / "Manga_Metadata_Output"
    selected_host: str = "Catbox"
    theme: str = "dark"
    language: str = "pt-BR"
    json_update_mode: str = "add"  # "add", "replace", "smart"
    
    hosts: Dict[str, HostConfig] = {
        "Catbox": HostConfig(),
        "Imgur": HostConfig(enabled=False),
        "ImgBB": HostConfig(enabled=False),
        "Lensdump": HostConfig(enabled=False),
        "Pixeldrain": HostConfig(enabled=False),
        "Gofile": HostConfig(enabled=False),
        "ImageChest": HostConfig(enabled=False),
        "Imgbox": HostConfig(enabled=False)
    }
    
    github: Dict[str, str] = {
        "user": "",
        "token": "",
        "repo": "",
        "branch": "main",
        "folder": "metadata"  # Default folder for JSON files
    }


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self.load_config()
    
    def _get_config_path(self) -> Path:
        """Get platform-specific config path"""
        import sys
        if sys.platform == "win32":
            base = Path.home() / "AppData" / "Local"
        else:
            base = Path.home() / ".config"
        
        config_dir = base / "MangaUploaderPro"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"
    
    def load_config(self) -> AppConfig:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config = AppConfig(**data)
                    
                    # Ensure all default hosts are present
                    default_hosts = {
                        "Catbox": HostConfig(),
                        "Imgur": HostConfig(enabled=False),
                        "ImgBB": HostConfig(enabled=False),
                        "Lensdump": HostConfig(enabled=False),
                        "Pixeldrain": HostConfig(enabled=False),
                        "Gofile": HostConfig(enabled=False),
                        "ImageChest": HostConfig(enabled=False),
                        "Imgbox": HostConfig(enabled=False)
                    }
                    
                    # Add missing hosts
                    for host_name, default_config in default_hosts.items():
                        if host_name not in config.hosts:
                            config.hosts[host_name] = default_config
                            logger.debug(f"Added missing host config: {host_name}")
                    
                    return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Return default config
        return AppConfig()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.model_dump(), f, indent=2, default=str)
            logger.success("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get_host_config(self, host_name: str) -> Optional[HostConfig]:
        """Get configuration for a specific host"""
        return self.config.hosts.get(host_name)