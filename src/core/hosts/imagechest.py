import aiohttp
from pathlib import Path
from typing import Optional, List
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class ImageChestHost(BaseHost):
    """ImageChest hosting service - stable API for serious projects"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.api_url = "https://api.imagechest.com/v1/upload"
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to ImageChest"""
        if not self.api_key:
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error="ImageChest API key not configured"
            )
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = aiohttp.FormData()
            data.add_field('image', 
                          open(filepath, 'rb'), 
                          filename=filepath.name,
                          content_type='image/*')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            image_url = result['data']['url']
                            logger.debug(f"ImageChest upload successful: {image_url}")
                            return UploadResult(
                                filename=filepath.name,
                                url=image_url,
                                success=True
                            )
                        else:
                            error_msg = result.get('message', 'Unknown error')
                            return UploadResult(
                                filename=filepath.name,
                                url="",
                                success=False,
                                error=f"ImageChest API error: {error_msg}"
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
            logger.error(f"ImageChest upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Create album in ImageChest"""
        if not self.api_key or not image_ids:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            album_data = {
                'title': title,
                'description': description,
                'images': image_ids
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.imagechest.com/v1/albums", 
                    json=album_data, 
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            album_url = result['data']['url']
                            logger.debug(f"ImageChest album created: {album_url}")
                            return album_url
        except Exception as e:
            logger.error(f"ImageChest album creation failed: {e}")
        
        return None