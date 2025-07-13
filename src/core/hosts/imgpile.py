import httpx
from pathlib import Path
from typing import Optional, List
import asyncio
import base64
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseHost
from core.models import UploadResult


class ImgPileHost(BaseHost):
    """ImgPile REST API implementation"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://imgpile.com')
        self.api_key = config.get('api_key', '')  # Optional for some implementations
        self.client = httpx.AsyncClient(timeout=300.0)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to ImgPile with retry logic"""
        if not filepath.exists():
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error="File not found"
            )
        
        try:
            # Try multipart/form-data upload first
            upload_url = f"{self.base_url}/api/images"
            
            with open(filepath, 'rb') as f:
                files = {'file': (filepath.name, f, 'application/octet-stream')}
                data = {'title': filepath.stem}
                
                # Add API key if available
                if self.api_key:
                    data['api_key'] = self.api_key
                
                response = await self.client.post(
                    upload_url,
                    data=data,
                    files=files
                )
                
                # If multipart fails, try base64 method
                if response.status_code != 200:
                    return await self._upload_base64(filepath)
                
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, dict):
                    if 'id' in result:
                        # Standard ImgPile response
                        image_id = result['id']
                        extension = result.get('extension', filepath.suffix.lstrip('.'))
                        url = f"{self.base_url}/static/uploads/{image_id}.{extension}"
                        
                        return UploadResult(
                            url=url,
                            filename=filepath.name,
                            success=True
                        )
                    elif 'url' in result:
                        # Alternative response format
                        return UploadResult(
                            url=result['url'],
                            filename=filepath.name,
                            success=True
                        )
                
                return UploadResult(
                    url="",
                    filename=filepath.name,
                    success=False,
                    error="Unexpected response format"
                )
                
        except Exception as e:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error=str(e)
            )
    
    async def _upload_base64(self, filepath: Path) -> UploadResult:
        """Fallback method using base64 encoding"""
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode('utf-8')
                
                # Create data URI
                mime_type = self._get_mime_type(filepath.suffix)
                data_uri = f"data:{mime_type};base64,{base64_data}"
                
                payload = {
                    'name': filepath.stem,
                    'source': data_uri
                }
                
                if self.api_key:
                    payload['api_key'] = self.api_key
                
                upload_url = f"{self.base_url}/api/images"
                response = await self.client.post(
                    upload_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if 'id' in result:
                    image_id = result['id']
                    extension = result.get('extension', filepath.suffix.lstrip('.'))
                    url = f"{self.base_url}/static/uploads/{image_id}.{extension}"
                    
                    return UploadResult(
                        url=url,
                        filename=filepath.name,
                        success=True
                    )
                
                return UploadResult(
                    url="",
                    filename=filepath.name,
                    success=False,
                    error="Base64 upload failed"
                )
                
        except Exception as e:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error=f"Base64 upload error: {str(e)}"
            )
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(extension.lower(), 'image/jpeg')
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """ImgPile doesn't support album creation in standard implementation"""
        return None
    
    async def get_image_info(self, image_id: str) -> Optional[dict]:
        """Get image information by ID"""
        try:
            url = f"{self.base_url}/api/images/{image_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()