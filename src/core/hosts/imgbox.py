from pathlib import Path
from typing import Optional, List
import asyncio
from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class ImgboxHost(BaseHost):
    """Imgbox hosting service using pyimgbox library"""
    
    def __init__(self, config):
        super().__init__(config)
        self._pyimgbox = None
    
    def _get_pyimgbox(self):
        """Lazy import of pyimgbox"""
        if self._pyimgbox is None:
            try:
                import pyimgbox
                self._pyimgbox = pyimgbox
            except ImportError:
                raise ImportError(
                    "pyimgbox library not installed. "
                    "Install with: pip install pyimgbox"
                )
        return self._pyimgbox
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Imgbox"""
        try:
            pyimgbox = self._get_pyimgbox()
            
            # Run in thread pool since pyimgbox is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_upload, 
                pyimgbox, 
                filepath
            )
            return result
            
        except ImportError as e:
            logger.error(f"Imgbox upload failed - missing dependency: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Imgbox upload failed for {filepath.name}: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    def _sync_upload(self, pyimgbox, filepath: Path):
        """Synchronous upload method"""
        try:
            # Upload single file
            submission = pyimgbox.upload(filepath)
            
            # Get the result
            for result in submission:
                if result['success']:
                    image_url = result['web_url']
                    logger.debug(f"Imgbox upload successful: {image_url}")
                    return UploadResult(
                        filename=filepath.name,
                        url=image_url,
                        success=True
                    )
                else:
                    error_msg = result.get('error', 'Unknown error')
                    return UploadResult(
                        filename=filepath.name,
                        url="",
                        success=False,
                        error=f"Imgbox error: {error_msg}"
                    )
            
            # No results
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error="No upload results received"
            )
            
        except Exception as e:
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Imgbox supports galleries but pyimgbox handles this automatically"""
        # pyimgbox creates galleries automatically when uploading multiple files
        return None