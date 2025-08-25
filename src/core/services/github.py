import httpx
import base64
from pathlib import Path
from typing import Optional
from loguru import logger


class GitHubService:
    """Service for saving metadata to GitHub"""
    
    def __init__(self, token: str = "", repo: str = "", branch: str = "main"):
        # Clean and validate inputs (remove ALL problematic characters)
        import re
        self.token = re.sub(r'[^\x20-\x7E]', '', str(token)).strip()  # Keep only printable ASCII
        self.repo = re.sub(r'[^\x20-\x7E]', '', str(repo)).strip()    # Keep only printable ASCII
        self.branch = re.sub(r'[^\x20-\x7E]', '', str(branch)).strip() # Keep only printable ASCII
        
        # Set defaults if empty
        if not self.token:
            self.token = ""
            logger.warning("GitHub token not configured")
        if not self.repo:
            self.repo = ""
            logger.warning("GitHub repository not configured")
        if self.repo and '/' not in self.repo:
            logger.warning("Repository should be in format 'owner/repo'")
        if not self.branch:
            self.branch = "main"
            
        self.configured = bool(self.token and self.repo and '/' in self.repo)
        
        if self.configured:
            self.client = httpx.AsyncClient(
                base_url="https://api.github.com",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=30.0
            )
        else:
            self.client = None
    
    async def upload_file(self, file_path: Path, remote_path: str, commit_message: str) -> bool:
        """Upload a file to GitHub repository"""
        if not self.configured:
            logger.warning("GitHub not configured - cannot upload file")
            return False
            
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            # Get current file SHA if exists
            sha = await self._get_file_sha(remote_path)
            
            # Read file content and clean any JSON corruption
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If this is a JSON file, clean any corruption before upload
            if file_path.suffix.lower() == '.json':
                try:
                    import json
                    from utils.json_updater import JSONUpdater
                    
                    data = json.loads(content)
                    clean_data = JSONUpdater.clean_corrupted_json(data)
                    content = json.dumps(clean_data, indent=2, ensure_ascii=False)
                    logger.info("JSON cleaned before GitHub upload")
                except Exception as e:
                    logger.warning(f"Could not clean JSON before upload: {e}")
                    # Continue with original content if cleaning fails
            
            # Encode content
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # Prepare request data
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": self.branch
            }
            
            if sha:
                data["sha"] = sha
            
            # Upload file
            response = await self.client.put(
                f"/repos/{self.repo}/contents/{remote_path}",
                json=data
            )
            
            if response.status_code in [200, 201]:
                logger.success(f"File uploaded to GitHub: {remote_path}")
                return True
            else:
                logger.error(f"GitHub upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading to GitHub: {e}")
            return False
    
    async def upload_content(self, repo: str, file_path: str, content: str, commit_message: str) -> bool:
        """Upload content directly to GitHub repository"""
        if not self.configured:
            logger.warning("GitHub not configured - cannot upload content")
            return False
        
        # Sanitize inputs
        import re
        repo = re.sub(r'[^\x20-\x7E]', '', str(repo)).strip()
        file_path = re.sub(r'[^\x20-\x7E]', '', str(file_path)).strip()
        commit_message = re.sub(r'[^\x20-\x7E]', '', str(commit_message)).strip()
        
        logger.debug(f"Uploading to GitHub - repo: '{repo}', file: '{file_path}', token configured: {bool(self.token)}")
            
        try:
            # Get existing file SHA if file exists
            existing_sha = await self._get_file_sha_for_repo(repo, file_path)
            
            # Encode content
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')
            
            # Prepare data
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": self.branch
            }
            
            if existing_sha:
                data["sha"] = existing_sha
            
            # Upload to GitHub
            response = await self.client.put(
                f"/repos/{repo}/contents/{file_path}",
                json=data
            )
            
            if response.status_code in [200, 201]:
                logger.success(f"Content uploaded to GitHub: {file_path}")
                return True
            elif response.status_code == 404:
                logger.error(f"Repository '{repo}' not found. Check if repository exists and token has access.")
                return False
            elif response.status_code == 401:
                logger.error(f"GitHub authentication failed. Check if token is valid.")
                return False
            elif response.status_code == 403:
                logger.error(f"GitHub access forbidden. Check if token has write permissions to '{repo}'.")
                return False
            else:
                logger.error(f"GitHub content upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading content to GitHub: {e}")
            return False
    
    async def _get_file_sha_for_repo(self, repo: str, remote_path: str) -> Optional[str]:
        """Get SHA of existing file in specific repo"""
        # Sanitize inputs
        import re
        repo = re.sub(r'[^\x20-\x7E]', '', str(repo)).strip()
        remote_path = re.sub(r'[^\x20-\x7E]', '', str(remote_path)).strip()
        
        try:
            response = await self.client.get(
                f"/repos/{repo}/contents/{remote_path}",
                params={"ref": self.branch}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("sha")
            else:
                return None
                
        except Exception:
            return None
    
    async def _get_file_sha(self, remote_path: str) -> Optional[str]:
        """Get SHA of existing file"""
        try:
            response = await self.client.get(
                f"/repos/{self.repo}/contents/{remote_path}",
                params={"ref": self.branch}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("sha")
                
        except Exception:
            pass
        
        return None
    
    async def create_pull_request(self, title: str, body: str, head_branch: str) -> Optional[str]:
        """Create a pull request"""
        try:
            response = await self.client.post(
                f"/repos/{self.repo}/pulls",
                json={
                    "title": title,
                    "body": body,
                    "head": head_branch,
                    "base": self.branch
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                return data.get("html_url")
                
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
        
        return None
    
    async def list_files(self, repo: str, path: str = "") -> list:
        """List files and folders in a repository path"""
        if not self.configured:
            logger.warning("GitHub not configured - cannot list files")
            return []
        
        # Sanitize inputs
        import re
        repo = re.sub(r'[^\x20-\x7E]', '', str(repo)).strip()
        path = re.sub(r'[^\x20-\x7E]', '', str(path)).strip()
            
        try:
            url = f"/repos/{repo}/contents"
            if path:
                url += f"/{path}"
            
            response = await self.client.get(
                url,
                params={"ref": self.branch}
            )
            
            if response.status_code == 200:
                data = response.json()
                items = []
                
                for item in data:
                    items.append({
                        "name": item["name"],
                        "path": item["path"],
                        "type": item["type"],  # "file" or "dir"
                        "size": item.get("size", 0),
                        "download_url": item.get("download_url")
                    })
                
                return items
            else:
                logger.error(f"GitHub list files failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing GitHub files: {e}")
            return []

    async def get_file_content(self, repo: str, file_path: str) -> str:
        """Get file content from repository"""
        if not self.configured:
            logger.warning("GitHub not configured - cannot get file content")
            return ""
        
        # Sanitize inputs
        import re
        repo = re.sub(r'[^\x20-\x7E]', '', str(repo)).strip()
        file_path = re.sub(r'[^\x20-\x7E]', '', str(file_path)).strip()
            
        try:
            url = f"/repos/{repo}/contents/{file_path}"
            
            response = await self.client.get(
                url,
                params={"ref": self.branch}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("encoding") == "base64":
                    content = base64.b64decode(data["content"]).decode('utf-8')
                    return content
                else:
                    return data.get("content", "")
            else:
                logger.error(f"GitHub get file content failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting GitHub file content: {e}")
            return ""

    async def list_folders(self, path: str = "") -> list:
        """List folders in the repository"""
        try:
            url = f"/repos/{self.repo}/contents"
            if path:
                url += f"/{path}"
            
            response = await self.client.get(
                url,
                params={"ref": self.branch}
            )
            
            if response.status_code == 200:
                data = response.json()
                folders = []
                
                # Don't add ".." option - it causes confusion
                
                # Add folders from response
                for item in data:
                    if item.get("type") == "dir":
                        folders.append({
                            "name": item["name"],
                            "path": item["path"],
                            "type": "dir"
                        })
                
                return folders
            else:
                logger.error(f"GitHub list folders failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing GitHub folders: {e}")
            return []
    
    async def close(self):
        """Properly close the HTTP client"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        if hasattr(self, 'client') and self.client and not self.client.is_closed:
            # Schedule cleanup in the event loop if available
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except RuntimeError:
                # No event loop available, client will be cleaned up by GC
                pass