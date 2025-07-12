import httpx
import base64
from pathlib import Path
from typing import Optional
from loguru import logger


class GitHubService:
    """Service for saving metadata to GitHub"""
    
    def __init__(self, token: str, repo: str, branch: str = "main"):
        # Clean and validate inputs (remove problematic characters)
        self.token = str(token).strip().replace('\n', '').replace('\r', '').replace('\t', '')
        self.repo = str(repo).strip().replace('\n', '').replace('\r', '').replace('\t', '')
        self.branch = str(branch).strip().replace('\n', '').replace('\r', '').replace('\t', '')
        
        # Validate required fields
        if not self.token:
            raise ValueError("GitHub token is required")
        if not self.repo:
            raise ValueError("GitHub repository is required")
        if '/' not in self.repo:
            raise ValueError("Repository must be in format 'owner/repo'")
        if not self.branch:
            self.branch = "main"
        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
    
    async def upload_file(self, file_path: Path, remote_path: str, commit_message: str) -> bool:
        """Upload a file to GitHub repository"""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            # Get current file SHA if exists
            sha = await self._get_file_sha(remote_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
                
                # Add root option
                if path:
                    folders.append({
                        "name": "..",
                        "path": "/".join(path.split("/")[:-1]) if "/" in path else "",
                        "type": "dir"
                    })
                
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
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()