import httpx
from pathlib import Path
from typing import Optional, List
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseHost
from core.models import UploadResult


class CatboxHost(BaseHost):
    """Modern async Catbox.moe implementation"""
    
    API_URL = "https://catbox.moe/user/api.php"
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.userhash = config.get('userhash', '')
        self.client = httpx.AsyncClient(timeout=300.0)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Catbox with retry logic"""
        if not filepath.exists():
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error="File not found"
            )
        
        try:
            with open(filepath, 'rb') as f:
                files = {'fileToUpload': (filepath.name, f, 'application/octet-stream')}
                data = {
                    'reqtype': 'fileupload',
                    'userhash': self.userhash
                }
                
                response = await self.client.post(
                    self.API_URL,
                    data=data,
                    files=files
                )
                response.raise_for_status()
                
                url = response.text.strip()
                return UploadResult(
                    url=url,
                    filename=filepath.name,
                    success=True
                )
                
        except Exception as e:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Create Catbox album"""
        if not image_ids:
            return None
        
        try:
            data = {
                'reqtype': 'createalbum',
                'userhash': self.userhash,
                'title': title,
                'desc': description,
                'files': ' '.join(image_ids)
            }
            
            response = await self.client.post(self.API_URL, data=data)
            response.raise_for_status()
            return response.text.strip()
            
        except Exception:
            return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()