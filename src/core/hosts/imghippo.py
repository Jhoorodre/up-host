import httpx
from pathlib import Path
from typing import Optional, List
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseHost
from core.models import UploadResult


class ImgHippoHost(BaseHost):
    """ImgHippo API v1 implementation"""
    
    UPLOAD_URL = "https://api.imghippo.com/v1/upload"
    DELETE_URL = "https://api.imghippo.com/v1/delete"
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.client = httpx.AsyncClient(timeout=300.0)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to ImgHippo with retry logic"""
        if not filepath.exists():
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error="File not found"
            )
        
        if not self.api_key:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error="API key not configured"
            )
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filepath.name, f, 'application/octet-stream')}
                data = {
                    'api_key': self.api_key,
                    'title': filepath.stem
                }
                
                response = await self.client.post(
                    self.UPLOAD_URL,
                    data=data,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('success'):
                    # Use view_url for direct image access
                    url = result['data']['view_url']
                    return UploadResult(
                        url=url,
                        filename=filepath.name,
                        success=True
                    )
                else:
                    return UploadResult(
                        url="",
                        filename=filepath.name,
                        success=False,
                        error=result.get('message', 'Upload failed')
                    )
                
        except Exception as e:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """ImgHippo doesn't support album creation, return None"""
        return None
    
    async def delete_image(self, image_url: str) -> bool:
        """Delete image from ImgHippo"""
        if not self.api_key or not image_url:
            return False
        
        try:
            data = {
                'api_key': self.api_key,
                'Url': image_url
            }
            
            response = await self.client.post(self.DELETE_URL, data=data)
            response.raise_for_status()
            
            result = response.json()
            return result.get('status') == 200
            
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()