import asyncio
import tempfile
import time
from pathlib import Path
from typing import Optional, List

from loguru import logger

from .base import BaseHost
from core.models import UploadResult


class ImgboxHost(BaseHost):
    """Imgbox hosting service using pyimgbox library with async generator support"""
    
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
    
    def _get_session_cookie(self) -> Optional[str]:
        """Get session cookie from config"""
        if isinstance(self.config, dict):
            return self.config.get('session_cookie', '')
        elif hasattr(self.config, 'session_cookie'):
            return self.config.session_cookie
        return None
    
    def _convert_webp_to_jpg(self, filepath: Path) -> tuple[Path, Optional[object]]:
        """Convert WebP to JPG if needed (Imgbox doesn't support WebP)"""
        if filepath.suffix.lower() != '.webp':
            return filepath, None
        
        logger.debug("Converting WebP to JPG for Imgbox compatibility")
        try:
            from PIL import Image
            
            # Create temporary JPG file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            # Convert WebP to JPG
            with Image.open(filepath) as img:
                # Convert to RGB if needed (WebP might have transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(temp_path, 'JPEG', quality=95)
            
            logger.debug(f"WebP converted to temporary JPG: {temp_path}")
            return temp_path, temp_file
            
        except ImportError:
            logger.warning("PIL not available for WebP conversion, uploading WebP directly")
            return filepath, None
        except Exception as e:
            logger.warning(f"WebP conversion failed: {e}, uploading WebP directly")
            return filepath, None
    
    def _cleanup_temp_file(self, temp_file: object, temp_path: Path):
        """Clean up temporary file with retry mechanism"""
        if not temp_file:
            return
        
        for attempt in range(3):
            try:
                time.sleep(0.1)  # Small delay to ensure file is released
                temp_path.unlink()
                logger.debug("Temporary JPG file cleaned up")
                break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    logger.debug(f"Temporary file will be cleaned by OS: {temp_path}")
                else:
                    time.sleep(0.5)  # Wait before retry
    
    async def _collect_submissions_async(self, gallery, filepath: Path) -> List:
        """Collect submissions using async generator"""
        result = []
        async for submission in gallery.add([filepath]):
            result.append(submission)
        return result
    
    def _upload_to_gallery(self, pyimgbox, filepath: Path) -> List:
        """Upload file to Imgbox gallery using async generator"""
        session_cookie = self._get_session_cookie()
        
        if session_cookie:
            logger.debug("Using session cookie for authentication")
        else:
            logger.debug("Using anonymous upload")
        
        # Create gallery for upload
        gallery_title = f"Upload {filepath.stem}"
        logger.debug(f"Creating gallery with title: {gallery_title}")
        gallery = pyimgbox.Gallery(title=gallery_title)
        logger.debug(f"Gallery created: {gallery}")
        
        # Upload using async generator
        logger.debug("Starting file upload with async generator...")
        logger.debug(f"Adding file to gallery: {filepath}")
        
        try:
            loop = asyncio.get_event_loop()
            submissions = loop.run_until_complete(
                self._collect_submissions_async(gallery, filepath)
            )
        except RuntimeError:
            # No event loop, create one
            submissions = asyncio.run(
                self._collect_submissions_async(gallery, filepath)
            )
        
        logger.debug(f"Upload submissions received: {submissions}")
        return submissions
    
    def _process_submission(self, submission, filepath: Path) -> UploadResult:
        """Process submission object and return UploadResult"""
        logger.debug(f"Processing submission: {submission}")
        
        if hasattr(submission, 'success') and submission.success:
            image_url = getattr(submission, 'image_url', '') or getattr(submission, 'url', '')
            logger.success(f"Imgbox upload successful: {image_url}")
            return UploadResult(
                filename=filepath.name,
                url=image_url,
                success=True
            )
        else:
            error_msg = getattr(submission, 'error', 'Unknown error')
            logger.error(f"Imgbox upload failed: {error_msg}")
            logger.error(f"Full submission data: {submission}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=f"Imgbox error: {error_msg}"
            )
    
    def _sync_upload(self, pyimgbox, filepath: Path) -> UploadResult:
        """Synchronous upload method"""
        try:
            logger.debug(f"_sync_upload called with filepath: {filepath}")
            
            submissions = self._upload_to_gallery(pyimgbox, filepath)
            
            if submissions:
                return self._process_submission(submissions[0], filepath)
            else:
                logger.error("No upload results received from Imgbox")
                return UploadResult(
                    filename=filepath.name,
                    url="",
                    success=False,
                    error="No upload results received"
                )
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Imgbox"""
        try:
            logger.debug(f"Starting Imgbox upload for: {filepath}")
            pyimgbox = self._get_pyimgbox()
            logger.debug("pyimgbox library loaded successfully")
            
            # Convert WebP to JPG if needed
            upload_path, temp_file = self._convert_webp_to_jpg(filepath)
            
            # Run upload in thread pool since pyimgbox is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_upload, 
                pyimgbox, 
                upload_path
            )
            
            # Clean up temporary file
            if temp_file and upload_path != filepath:
                self._cleanup_temp_file(temp_file, upload_path)
            
            # Update result with original filename
            if result and upload_path != filepath:
                result.filename = filepath.name
            
            logger.debug(f"Upload completed with result: {result}")
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
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return UploadResult(
                filename=filepath.name,
                url="",
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Imgbox supports galleries but pyimgbox handles this automatically"""
        return None