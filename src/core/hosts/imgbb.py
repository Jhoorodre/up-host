import aiohttp
from pathlib import Path
from typing import Optional, List
import base64
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class ImgBBHost(BaseHost):
    """ImgBB image hosting service"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.api_url = "https://api.imgbb.com/1/upload"
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to ImgBB"""
        if not self.api_key:
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error="ImgBB API key not configured"
            )
        
        try:
            # Read and encode image
            with open(filepath, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            data = {
                'key': self.api_key,
                'image': image_data,
                'name': filepath.stem
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            image_url = result['data']['url']
                            logger.debug(f"ImgBB upload successful: {image_url}")
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
                                error=f"ImgBB API error: {error_msg}"
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
            logger.error(f"ImgBB upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """ImgBB doesn't support album creation via API"""
        return None