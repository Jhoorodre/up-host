import aiohttp
from pathlib import Path
from typing import Optional, List
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class GofileHost(BaseHost):
    """Gofile hosting service - good for multiple files"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = "https://store1.gofile.io/uploadFile"
        self.get_server_url = "https://api.gofile.io/getServer"
    
    async def _get_upload_server(self):
        """Get the best upload server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.get_server_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('status') == 'ok':
                            server = result['data']['server']
                            return f"https://{server}.gofile.io/uploadFile"
        except Exception as e:
            logger.warning(f"Failed to get Gofile server, using default: {e}")
        
        return self.api_url
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Gofile"""
        try:
            upload_url = await self._get_upload_server()
            
            data = aiohttp.FormData()
            data.add_field('file', 
                          open(filepath, 'rb'), 
                          filename=filepath.name)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('status') == 'ok':
                            file_code = result['data']['code']
                            download_page = result['data']['downloadPage']
                            # Gofile gives a download page, not direct link
                            logger.debug(f"Gofile upload successful: {download_page}")
                            return UploadResult(
                                filename=filepath.name,
                                url=download_page,
                                success=True
                            )
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            return UploadResult(
                                filename=filepath.name,
                                url="",
                                success=False,
                                error=f"Gofile API error: {error_msg}"
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
            logger.error(f"Gofile upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Gofile supports folders/albums but requires additional API calls"""
        # This would require folder creation API which is more complex
        return None