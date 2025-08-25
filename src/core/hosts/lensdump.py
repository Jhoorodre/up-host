import aiohttp
from pathlib import Path
from typing import Optional, List
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class LensdumpHost(BaseHost):
    """Lensdump image hosting service - preserves image quality"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = "https://lensdump.com/api/1/upload"
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Lensdump"""
        try:
            data = aiohttp.FormData()
            data.add_field('source', 
                          open(filepath, 'rb'), 
                          filename=filepath.name,
                          content_type='image/*')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('status_code') == 200:
                            image_url = result['image']['url']
                            logger.debug(f"Lensdump upload successful: {image_url}")
                            return UploadResult(
                                filename=filepath.name,
                                url=image_url,
                                success=True
                            )
                        else:
                            error_msg = result.get('error', {}).get('message', 'Unknown error')
                            return UploadResult(
                                filename=filepath.name,
                                url="",
                                success=False,
                                error=f"Lensdump API error: {error_msg}"
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
            logger.error(f"Lensdump upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Lensdump doesn't support album creation via API"""
        return None