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
    
    async def _get_direct_link(self, session: aiohttp.ClientSession, file_code: str) -> Optional[str]:
        """Get direct download link from file code"""
        try:
            # Method 1: Try content API to get file info
            content_url = f"https://api.gofile.io/getContent?contentId={file_code}"
            
            async with session.get(content_url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('status') == 'ok' and 'data' in result:
                        data = result['data']
                        
                        # Check if it's a file directly
                        if data.get('type') == 'file':
                            # Direct file access
                            direct_link = data.get('directLink')
                            if direct_link:
                                logger.debug(f"Found Gofile direct link: {direct_link}")
                                return direct_link
                            
                            # Fallback: construct from file info
                            server = data.get('server', 'store1')
                            filename = data.get('name', '')
                            if filename:
                                direct_url = f"https://{server}.gofile.io/download/{file_code}/{filename}"
                                logger.debug(f"Constructed Gofile direct link: {direct_url}")
                                return direct_url
                        
                        # If it's a folder, look for files inside
                        contents = data.get('contents', {})
                        for content_id, content_info in contents.items():
                            if content_info.get('type') == 'file':
                                direct_link = content_info.get('directLink')
                                if direct_link:
                                    logger.debug(f"Found Gofile direct link in folder: {direct_link}")
                                    return direct_link
                                
                                # Construct direct link
                                server = content_info.get('server', 'store1')
                                filename = content_info.get('name', '')
                                if filename:
                                    direct_url = f"https://{server}.gofile.io/download/{content_id}/{filename}"
                                    logger.debug(f"Constructed Gofile direct link from folder: {direct_url}")
                                    return direct_url
            
            # Method 2: Try alternative direct link format
            # Some Gofile files can be accessed directly via download endpoint
            direct_url_alt = f"https://store1.gofile.io/download/direct/{file_code}"
            logger.debug(f"Trying alternative Gofile direct link: {direct_url_alt}")
            
            # Test if the alternative URL works (HEAD request)
            async with session.head(direct_url_alt) as test_response:
                if test_response.status == 200:
                    return direct_url_alt
                        
        except Exception as e:
            logger.warning(f"Failed to get Gofile direct link for {file_code}: {e}")
        
        return None
    
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
                            
                            # Try to get direct link from file info
                            direct_url = await self._get_direct_link(session, file_code)
                            final_url = direct_url if direct_url else download_page
                            
                            logger.debug(f"Gofile upload successful: {final_url}")
                            return UploadResult(
                                filename=filepath.name,
                                url=final_url,
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