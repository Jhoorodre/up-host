from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

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
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def upload_with_limit(image: Path):
            async with semaphore:
                await asyncio.sleep(self.rate_limit)
                return await self.upload_image(image)
        
        # Upload all images concurrently
        tasks = [upload_with_limit(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_uploads = []
        failed_uploads = []
        image_ids = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_uploads.append(images[i].name)
            elif isinstance(result, UploadResult):
                if result.success:
                    successful_uploads.append(result.url)
                    # Extract ID from URL for album creation
                    image_id = result.url.split('/')[-1]
                    image_ids.append(image_id)
                else:
                    failed_uploads.append(result.filename)
        
        # Create album if we have successful uploads
        album_url = ""
        if successful_uploads and hasattr(self, 'create_album'):
            album_url = await self.create_album(
                title=f"{chapter_name}",
                description=f"Chapter {chapter_name}",
                image_ids=image_ids
            ) or ""
        
        return ChapterUploadResult(
            chapter_name=chapter_name,
            album_url=album_url,
            image_urls=successful_uploads,
            failed_uploads=failed_uploads,
            success=len(failed_uploads) == 0
        )
    
    def __str__(self):
        return f"{self.name}Host"