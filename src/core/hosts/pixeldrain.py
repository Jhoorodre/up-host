import aiohttp
from pathlib import Path
from typing import Optional, List
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class PixeldrainHost(BaseHost):
    """Pixeldrain file hosting service - fast uploads with generous limits"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = "https://pixeldrain.com/api/file"
        self.api_key = config.get('api_key', '')  # Optional for basic usage
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Pixeldrain"""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Basic {self.api_key}'
            
            data = aiohttp.FormData()
            data.add_field('file', 
                          open(filepath, 'rb'), 
                          filename=filepath.name)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data, headers=headers) as response:
                    if response.status == 201:  # Pixeldrain returns 201 for successful uploads
                        result = await response.json()
                        file_id = result.get('id')
                        if file_id:
                            # Pixeldrain direct link format
                            image_url = f"https://pixeldrain.com/api/file/{file_id}"
                            logger.debug(f"Pixeldrain upload successful: {image_url}")
                            return UploadResult(
                                filename=filepath.name,
                                url=image_url,
                                success=True
                            )
                        else:
                            return UploadResult(
                                filename=filepath.name,
                                url="",
                                success=False,
                                error="No file ID in response"
                            )
                    else:
                        error_text = await response.text()
                        return UploadResult(
                            filename=filepath.name,
                            url="",
                            success=False,
                            error=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"Pixeldrain upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Pixeldrain doesn't support album creation via API"""
        return None