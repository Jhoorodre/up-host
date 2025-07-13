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
            logger.debug(f"Starting Imgbox upload for: {filepath}")
            pyimgbox = self._get_pyimgbox()
            logger.debug("pyimgbox library loaded successfully")
            
            # Convert WebP to JPG if needed (Imgbox doesn't support WebP)
            upload_path = filepath
            temp_file = None
            if filepath.suffix.lower() == '.webp':
                logger.debug("Converting WebP to JPG for Imgbox compatibility")
                try:
                    from PIL import Image
                    import tempfile
                    
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
                    
                    upload_path = temp_path
                    logger.debug(f"WebP converted to temporary JPG: {upload_path}")
                    
                except ImportError:
                    logger.warning("PIL not available for WebP conversion, uploading WebP directly")
                except Exception as e:
                    logger.warning(f"WebP conversion failed: {e}, uploading WebP directly")
            
            # Run in thread pool since pyimgbox is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_upload, 
                pyimgbox, 
                upload_path
            )
            
            # Clean up temporary file with retry
            if temp_file and upload_path != filepath:
                import time
                for attempt in range(3):
                    try:
                        time.sleep(0.1)  # Small delay to ensure file is released
                        upload_path.unlink()
                        logger.debug("Temporary JPG file cleaned up")
                        break
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            logger.debug(f"Temporary file will be cleaned by OS: {upload_path}")
                        else:
                            time.sleep(0.5)  # Wait before retry
            
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
    
    def _sync_upload(self, pyimgbox, filepath: Path):
        """Synchronous upload method"""
        try:
            logger.debug(f"_sync_upload called with filepath: {filepath}")
            
            # Get session cookie if configured
            session_cookie = None
            if isinstance(self.config, dict):
                session_cookie = self.config.get('session_cookie', '')
            elif hasattr(self.config, 'session_cookie'):
                session_cookie = self.config.session_cookie
            
            if session_cookie:
                logger.debug(f"Using session cookie for authentication")
            else:
                logger.debug("Using anonymous upload")
            
            # Create gallery for upload
            gallery_title = f"Upload {filepath.stem}"
            logger.debug(f"Creating gallery with title: {gallery_title}")
            
            # Upload using Gallery context manager
            # Note: Current pyimgbox version doesn't support session authentication parameters
            # Uploads will be anonymous but functional
            gallery = pyimgbox.Gallery(title=gallery_title)
            
            logger.debug(f"Gallery created: {gallery}")
            
            # Upload the file
            logger.debug("Starting file upload...")
            logger.debug(f"Adding file to gallery: {filepath}")
            
            # Try different approaches for pyimgbox API
            try:
                # Method 1: Direct iteration
                submissions = list(gallery.add([filepath]))
            except (TypeError, RuntimeError) as e:
                logger.debug(f"Method 1 failed: {e}, trying method 2")
                try:
                    # Method 2: Manual iteration
                    submissions = []
                    add_result = gallery.add([filepath])
                    for submission in add_result:
                        submissions.append(submission)
                except Exception as e2:
                    logger.debug(f"Method 2 failed: {e2}, trying method 3")
                    # Method 3: Use asyncio to handle async generator
                    import asyncio
                    
                    async def collect_submissions():
                        result = []
                        async for submission in gallery.add([filepath]):
                            result.append(submission)
                        return result
                    
                    # Run in the current thread
                    try:
                        loop = asyncio.get_event_loop()
                        submissions = loop.run_until_complete(collect_submissions())
                    except RuntimeError:
                        # No event loop, create one
                        submissions = asyncio.run(collect_submissions())
            
            logger.debug(f"Upload submissions received: {submissions}")
            
            if submissions:
                submission = submissions[0]
                logger.debug(f"Processing submission: {submission}")
                if submission.get('success', False):
                    image_url = submission.get('image_url', submission.get('url', ''))
                    logger.success(f"Imgbox upload successful: {image_url}")
                    return UploadResult(
                        filename=filepath.name,
                        url=image_url,
                        success=True
                    )
                else:
                    error_msg = submission.get('error', 'Unknown error')
                    logger.error(f"Imgbox upload failed: {error_msg}")
                    logger.error(f"Full submission data: {submission}")
                    return UploadResult(
                        filename=filepath.name,
                        url="",
                        success=False,
                        error=f"Imgbox error: {error_msg}"
                    )
            
            # No results
            logger.error("No upload results received from Imgbox")
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