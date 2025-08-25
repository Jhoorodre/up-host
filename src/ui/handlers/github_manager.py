"""GitHub integration management handler for UI backend"""

import asyncio
from typing import Optional, Dict, Any, List
from PySide6.QtCore import QObject, Signal, Property, Slot
from core.config import ConfigManager
from core.services.github import GitHubService
from loguru import logger


class GitHubManager(QObject):
    """Handles all GitHub integration operations"""
    
    githubConfigChanged = Signal()
    githubStatusChanged = Signal(str)
    githubUploadProgress = Signal(str, int)
    githubUploadCompleted = Signal(str)
    githubUploadFailed = Signal(str, str)
    githubFoldersChanged = Signal(list)  # CRITICAL: Add signal with folder data
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.github_service: Optional[GitHubService] = None
        self._github_folders = ["metadata"]  # CRITICAL: Store folders in GitHubManager
        self._init_github_service()
    
    def __del__(self):
        """Cleanup when manager is destroyed"""
        if self.github_service:
            # Schedule cleanup in the event loop if available
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.github_service.close())
            except RuntimeError:
                # No event loop available, client will be cleaned up by GC
                pass
    
    # GitHub Configuration Properties
    @Property(bool, notify=githubConfigChanged)
    def githubEnabled(self):
        return self.config_manager.config.github.get("enabled", False)
    
    @Property(str, notify=githubConfigChanged)
    def githubToken(self):
        return self.config_manager.config.github.get("token", "")
    
    @Property(str, notify=githubConfigChanged)
    def githubRepo(self):
        return self.config_manager.config.github.get("repo", "")
    
    @Property(str, notify=githubConfigChanged)
    def githubBranch(self):
        return self.config_manager.config.github.get("branch", "main")
    
    @Property(str, notify=githubConfigChanged)
    def githubFolder(self):
        return self.config_manager.config.github.get("folder", "")
    
    @Property(bool, notify=githubConfigChanged)
    def githubAutoUpload(self):
        return self.config_manager.config.github.get("auto_upload", False)
    
    @Property(str, notify=githubConfigChanged)
    def githubCommitMessage(self):
        return self.config_manager.config.github.get("commit_message", "Update manga metadata")
    
    # Indexador Configuration Properties
    @Property(bool, notify=githubConfigChanged)
    def indexadorEnabled(self):
        return self.config_manager.config.indexador.get("enabled", False) if hasattr(self.config_manager.config, 'indexador') else False
    
    @Property(str, notify=githubConfigChanged)
    def indexadorGroupName(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("group_name", "")
        return ""
    
    @Property(str, notify=githubConfigChanged)
    def indexadorDescription(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("description", "")
        return ""
    
    @Property(str, notify=githubConfigChanged)
    def indexadorDiscord(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("discord", "")
        return ""
    
    @Property(str, notify=githubConfigChanged)
    def indexadorTelegram(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("telegram", "")
        return ""
    
    @Property(str, notify=githubConfigChanged)
    def indexadorWebsite(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("website", "")
        return ""
    
    @Property(str, notify=githubConfigChanged)
    def indexadorUrlTemplate(self):
        if hasattr(self.config_manager.config, 'indexador'):
            return self.config_manager.config.indexador.get("url_template", "https://cdn.jsdelivr.net/gh/{repo}@{branch}/{file}")
        return "https://cdn.jsdelivr.net/gh/{repo}@{branch}/{file}"
    
    def _init_github_service(self):
        """Initialize GitHub service if configured"""
        try:
            # Close existing service if any
            if self.github_service:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self.github_service.close())
                except RuntimeError:
                    pass  # No event loop available
            
            github_config = self.config_manager.config.github
            token = github_config.get("token", "").strip()
            repo = github_config.get("repo", "").strip()
            
            # Initialize service if we have both token and repo
            if token and repo and self.validate_github_repo(repo):
                self.github_service = GitHubService(
                    token=token,
                    repo=repo,
                    branch=github_config.get("branch", "main")
                )
                logger.info("GitHub service initialized successfully")
                logger.debug(f"GitHub config: repo='{repo}', branch='{github_config.get('branch', 'main')}'")
            else:
                self.github_service = None
                logger.debug(f"GitHub service not initialized - token: {'set' if token else 'missing'}, "
                           f"repo: '{repo}', valid_repo: {self.validate_github_repo(repo) if repo else False}")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub service: {e}")
            self.github_service = None
    
    def update_github_config(self, config_dict: Dict[str, Any]):
        """Update GitHub configuration from QML - CRITICAL FOR CONFIGURATION UPDATES"""
        try:
            github_config = self.config_manager.config.github
            config_changed = False
            
            # Update GitHub settings with proper dict access - CRITICAL
            if "githubToken" in config_dict:
                token = str(config_dict["githubToken"]).strip()
                github_config["token"] = token
                config_changed = True
                logger.debug(f"Updated GitHub token (length: {len(token)})")
            
            if "githubRepo" in config_dict:
                repo = str(config_dict["githubRepo"]).strip()
                github_config["repo"] = repo
                config_changed = True
                logger.debug(f"Updated GitHub repo: {repo}")
            
            if "githubBranch" in config_dict:
                branch = str(config_dict["githubBranch"]).strip() or "main"
                github_config["branch"] = branch
                config_changed = True
                logger.debug(f"Updated GitHub branch: {branch}")
            
            if "githubFolder" in config_dict:
                folder = str(config_dict["githubFolder"]).strip()
                github_config["folder"] = folder
                config_changed = True
                logger.debug(f"Updated GitHub folder: {folder}")
            
            if "githubAutoUpload" in config_dict:
                auto_upload = bool(config_dict["githubAutoUpload"])
                github_config["auto_upload"] = auto_upload
                config_changed = True
                logger.debug(f"Updated GitHub auto upload: {auto_upload}")
            
            if "githubCommitMessage" in config_dict:
                commit_msg = str(config_dict["githubCommitMessage"]).strip() or "Update manga metadata"
                github_config["commit_message"] = commit_msg
                config_changed = True
                logger.debug(f"Updated GitHub commit message: {commit_msg}")
            
            # Handle GitHub enabled flag
            if "githubEnabled" in config_dict:
                enabled = bool(config_dict["githubEnabled"])
                github_config["enabled"] = enabled
                config_changed = True
                logger.debug(f"Updated GitHub enabled: {enabled}")
            
            # Update Indexador settings if they exist in config
            if hasattr(self.config_manager.config, 'indexador'):
                indexador_config = self.config_manager.config.indexador
                
                indexador_keys = [
                    "indexadorEnabled", "indexadorGroupName", "indexadorDescription",
                    "indexadorDiscord", "indexadorTelegram", "indexadorWebsite", 
                    "indexadorUrlTemplate"
                ]
                
                for key in indexador_keys:
                    if key in config_dict:
                        attr_name = key.replace("indexador", "").lower()
                        if attr_name == "enabled":
                            indexador_config[attr_name] = bool(config_dict[key])
                        else:
                            indexador_config[attr_name] = str(config_dict[key]).strip()
                        config_changed = True
                        logger.debug(f"Updated indexador {attr_name}: {config_dict[key]}")
            
            if config_changed:
                # Re-initialize GitHub service with new config
                self._init_github_service()
                self.githubConfigChanged.emit()
                logger.info("GitHub configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating GitHub config: {e}")
            raise
    
    @Slot(str, result=bool)
    def validate_github_token(self, token: str) -> bool:
        """Validate GitHub token"""
        try:
            # TODO: Implement actual token validation
            # This would require making a test API call
            return len(token.strip()) > 10 and token.startswith(('ghp_', 'github_pat_'))
        except Exception as e:
            logger.error(f"Error validating GitHub token: {e}")
            return False
    
    @Slot(str, result=bool)
    def validate_github_repo(self, repo: str) -> bool:
        """Validate GitHub repository format"""
        try:
            repo = repo.strip()
            if '/' not in repo:
                return False
            
            parts = repo.split('/')
            return len(parts) == 2 and all(part.strip() for part in parts)
        except Exception as e:
            logger.error(f"Error validating GitHub repo: {e}")
            return False
    
    @Slot(result=bool)
    def test_github_connection(self) -> bool:
        """Test GitHub connection"""
        try:
            if not self.github_service:
                return False
            
            # TODO: Implement actual async connection test in a proper async context
            return True
        except Exception as e:
            logger.error(f"Error testing GitHub connection: {e}")
            return False
    
    def upload_metadata(self, file_path: str, content: str, commit_message: str = None) -> bool:
        """Upload metadata file to GitHub"""
        try:
            if not self.github_service:
                logger.warning("GitHub service not available")
                return False
            
            if not commit_message:
                commit_message = self.config_manager.config.github.commit_message
            
            # Run async upload in current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Use ensure_future for running event loop
                future = asyncio.ensure_future(self._async_upload_metadata(file_path, content, commit_message))
                # Note: This returns immediately, actual upload happens async
                return True
            else:
                # Sync execution if no loop running
                return loop.run_until_complete(self._async_upload_metadata(file_path, content, commit_message))
            
        except Exception as e:
            logger.error(f"Error uploading metadata to GitHub: {e}")
            return False
    
    def generate_indexador_json(self) -> Dict[str, Any]:
        """Generate indexador JSON structure"""
        try:
            from datetime import datetime
            
            # Get indexador config if available
            if hasattr(self.config_manager.config, 'indexador'):
                indexador_config = self.config_manager.config.indexador
                
                indexador_data = {
                    "hub": {
                        "title": indexador_config.get("group_name", "Default Group"),
                        "description": indexador_config.get("description", "Manga upload group"),
                        "social": {
                            "discord": indexador_config.get("discord", ""),
                            "telegram": indexador_config.get("telegram", ""),
                            "website": indexador_config.get("website", "")
                        }
                    },
                    "statistics": {
                        "total_series": 0,
                        "total_chapters": 0,
                        "last_updated": datetime.now().isoformat()
                    },
                    "series": {}
                }
            else:
                # Fallback structure
                indexador_data = {
                    "hub": {
                        "title": "Default Group",
                        "description": "Manga upload group",
                        "social": {}
                    },
                    "statistics": {
                        "total_series": 0,
                        "total_chapters": 0,
                        "last_updated": datetime.now().isoformat()
                    },
                    "series": {}
                }
            
            return indexador_data
            
        except Exception as e:
            logger.error(f"Error generating indexador JSON: {e}")
            return {}
    
    def is_github_configured(self) -> bool:
        """Check if GitHub is properly configured"""
        try:
            config = self.config_manager.config.github
            token = config.get("token", "").strip()
            repo = config.get("repo", "").strip()
            
            # Consider GitHub configured if token and repo are provided
            # The enabled flag is optional (for backward compatibility)
            is_configured = (bool(token) and 
                           bool(repo) and
                           self.validate_github_repo(repo))
            
            logger.debug(f"GitHub configuration check: token={'***' if token else 'empty'}, "
                        f"repo='{repo}', configured={is_configured}")
            return is_configured
        except Exception as e:
            logger.error(f"Error checking GitHub configuration: {e}")
            return False
    
    def get_github_service(self) -> Optional[GitHubService]:
        """Get the GitHub service instance"""
        return self.github_service
    
    async def _async_upload_metadata(self, file_path: str, content: str, commit_message: str) -> bool:
        """Async method to upload metadata to GitHub"""
        try:
            if not self.github_service:
                logger.error("GitHub service not available")
                return False
            
            from pathlib import Path
            
            # Create a temporary file if content is provided instead of file_path
            if content and not Path(file_path).exists():
                temp_file = Path("/tmp") / f"temp_{Path(file_path).name}"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                file_path = str(temp_file)
            
            # Determine remote path
            github_folder = self.config_manager.config.github.get("folder", "")
            filename = Path(file_path).name
            remote_path = f"{github_folder}/{filename}" if github_folder else filename
            
            # Upload file
            success = await self.github_service.upload_file(
                Path(file_path), 
                remote_path, 
                commit_message
            )
            
            if success:
                self.githubUploadCompleted.emit(filename)
                logger.info(f"Successfully uploaded {filename} to GitHub")
            else:
                self.githubUploadFailed.emit(filename, "Upload failed")
                logger.error(f"Failed to upload {filename} to GitHub")
            
            return success
            
        except Exception as e:
            error_msg = f"Error uploading to GitHub: {e}"
            logger.error(error_msg)
            self.githubUploadFailed.emit(Path(file_path).name, error_msg)
            return False
    
    @Slot()
    def refreshGitHubFolders(self):
        """Load all folders from GitHub repository"""
        if not self.is_github_configured():
            logger.warning("GitHub not configured, cannot refresh folders")
            return
        
        # Start async folder loading
        asyncio.ensure_future(self._refresh_github_folders())
    
    async def _refresh_github_folders(self):
        """Load all folders from GitHub repository recursively"""
        try:
            if not self.github_service:
                logger.error("GitHub service not available")
                # CRITICAL: Emit fallback folders
                self._github_folders = ["", "metadata"]
                self.githubFoldersChanged.emit(self._github_folders)
                return
            
            logger.debug("Loading all GitHub folders recursively")
            
            all_folders = await self._get_all_folders_recursive(self.github_service, "")
            
            # Add default options and remove duplicates
            folder_options = ["", "metadata"] + sorted(set(all_folders))
            unique_folders = []
            seen = set()
            for folder in folder_options:
                if folder not in seen:
                    seen.add(folder)
                    unique_folders.append(folder)
            
            # CRITICAL: Store folders and emit signal with data
            self._github_folders = unique_folders
            self.githubFoldersChanged.emit(self._github_folders)
            logger.debug(f"Loaded {len(unique_folders)} GitHub folder options: {unique_folders[:10]}...")
            
        except Exception as e:
            logger.error(f"Error loading GitHub folders: {e}")
            # CRITICAL: Emit fallback folders on error
            self._github_folders = ["", "metadata"]
            self.githubFoldersChanged.emit(self._github_folders)
    
    async def _get_all_folders_recursive(self, github_service, path: str = "", max_depth: int = 3, current_depth: int = 0):
        """Recursively get all folders in the repository"""
        if current_depth >= max_depth:
            return []
        
        all_folders = []
        
        try:
            if hasattr(github_service, 'list_folders'):
                folders = await github_service.list_folders(path)
                
                for folder in folders:
                    if folder.get("type") == "dir" and folder.get("name") != "..":
                        folder_path = folder.get("path", "")
                        if folder_path:
                            all_folders.append(folder_path)
                            
                            # Recursively get subfolders
                            subfolders = await self._get_all_folders_recursive(
                                github_service, folder_path, max_depth, current_depth + 1
                            )
                            all_folders.extend(subfolders)
        except Exception as e:
            logger.warning(f"Error loading subfolders for {path}: {e}")
        
        return all_folders
    
    def select_folder(self, folder_path: str):
        """Select a GitHub folder and update configuration"""
        try:
            github_config = self.config_manager.config.github
            github_config["folder"] = folder_path
            self.config_manager.save_config()
            self.githubConfigChanged.emit()
            logger.info(f"GitHub folder selected: {folder_path}")
        except Exception as e:
            logger.error(f"Error selecting GitHub folder: {e}")
            raise
    
    def get_folders(self) -> List[str]:
        """Get current list of GitHub folders - CRITICAL for Backend access"""
        return self._github_folders.copy()
    
    @Property(list, notify=githubFoldersChanged)
    def githubFolders(self):
        """Property to expose folders to QML (if needed directly)"""
        return self._github_folders
    
    def upload_current_metadata(self):
        """Upload current metadata to GitHub (wrapper for backend integration)"""
        try:
            if not self.is_github_configured():
                logger.warning("GitHub not configured")
                return False
            
            # This will be called by the backend with actual metadata
            logger.info("GitHub metadata upload requested")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading metadata to GitHub: {e}")
            return False