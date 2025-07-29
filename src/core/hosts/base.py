from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from loguru import logger

from core.models import UploadResult, ChapterUploadResult


class BaseHost(ABC):
    """Base class for all image hosting services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Host', '')
        self.max_workers = config.get('max_workers', 5)
        self.rate_limit = config.get('rate_limit', 1.0)
    
    @abstractmethod
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload a single image to the host"""
        pass
    
    @abstractmethod
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Create an album with uploaded images"""
        pass
    
    async def upload_chapter(self, chapter_name: str, images: List[Path]) -> ChapterUploadResult:
        """Upload all images from a chapter"""
        logger.info(f"Starting upload for chapter '{chapter_name}' with {len(images)} images using {self.name}")
        logger.debug(f"Host config: max_workers={self.max_workers}, rate_limit={self.rate_limit}")
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def upload_with_limit(image: Path):
            async with semaphore:
                await asyncio.sleep(self.rate_limit)
                logger.debug(f"Uploading {image.name}...")
                try:
                    result = await self.upload_image(image)
                    if result.success:
                        logger.debug(f"✓ {image.name} uploaded successfully")
                    else:
                        logger.warning(f"✗ {image.name} upload failed: {result.error}")
                    return result
                except Exception as e:
                    logger.error(f"✗ Exception uploading {image.name}: {type(e).__name__}: {str(e)}")
                    raise
        
        # Upload all images concurrently
        tasks = [upload_with_limit(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_uploads = []
        failed_uploads = []
        image_ids = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                image_name = images[i].name
                logger.error(f"Upload exception for {image_name}: {type(result).__name__}: {str(result)}")
                failed_uploads.append(image_name)
            elif isinstance(result, UploadResult):
                if result.success:
                    successful_uploads.append(result.url)
                    # Extract ID from URL for album creation
                    image_id = result.url.split('/')[-1]
                    image_ids.append(image_id)
                else:
                    logger.error(f"Upload failed for {result.filename}: {result.error}")
                    failed_uploads.append(result.filename)
        
        # Create album if we have successful uploads
        album_url = ""
        if successful_uploads and hasattr(self, 'create_album'):
            logger.debug(f"Creating album for {len(successful_uploads)} images...")
            album_url = await self.create_album(
                title=f"{chapter_name}",
                description=f"Chapter {chapter_name}",
                image_ids=image_ids
            ) or ""
            if album_url:
                logger.info(f"Album created: {album_url}")
        
        # Log final results
        total_images = len(images)
        success_count = len(successful_uploads)
        failed_count = len(failed_uploads)
        
        if failed_count == 0:
            logger.success(f"Chapter '{chapter_name}' uploaded successfully: {success_count}/{total_images} images")
        else:
            logger.error(f"Chapter '{chapter_name}' upload completed with failures: {success_count}/{total_images} successful, {failed_count} failed")
            if failed_uploads:
                logger.error(f"Failed files: {', '.join(failed_uploads)}")
        
        return ChapterUploadResult(
            chapter_name=chapter_name,
            album_url=album_url,
            image_urls=successful_uploads,
            failed_uploads=failed_uploads,
            success=len(failed_uploads) == 0
        )
    
    def __str__(self):
        return f"{self.name}Host"